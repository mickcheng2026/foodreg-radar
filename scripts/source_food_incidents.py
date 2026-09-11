"""食安事件（各國）爬蟲 — 全球食安新聞 + 各國新聞事件

兩類來源（皆 RSS、純 stdlib、無需金鑰）：
1. Food Safety News — 全球食安專業新聞站
2. Google News RSS — 用關鍵字搜各國新聞，補抓「沒有官方公告、只有新聞」的食安事件
   - 英文：全球 outbreak / recall
   - 中文：台灣／華語圈 食品中毒、回收、污染（標題本身即中文，免翻譯）

設計：
- 每筆推斷國家/地區與病原標籤，產出結構化中文 ai_summary
- 以 URL + 標題正規化去重（跨來源同篇只留一筆；標題被追加子句也認得出來）
- Google News 結果以食安關鍵字過濾，濾掉政策/活動等雜訊
- 再以 is_noise() 濾掉意見專欄／解釋文／調查報告／政策修法等「非具體事件」，
  只留有明確產品／廠商／病原的召回與疫情（同一事件只留一則）
- build_data 以 URL 去重保留歷史 → 涵蓋隨每日 cron 累積
"""
from __future__ import annotations
import re
import xml.etree.ElementTree as ET
from common import fetch, clean_text, make_item, normalize_date

# 來源清單：kind=fsn 全收；kind=gnews 需通過食安關鍵字過濾
FEEDS = [
    # Food Safety News（美國媒體；未偵測到他國時預設美國）
    {"url": "https://www.foodsafetynews.com/feed/", "kind": "fsn", "default": "美國"},
    {"url": "https://www.foodsafetynews.com/tag/2026-outbreaks/feed/", "kind": "fsn", "default": "美國"},
    {"url": "https://www.foodsafetynews.com/tag/2025-outbreaks/feed/", "kind": "fsn", "default": "美國"},
    {"url": "https://www.foodsafetynews.com/tag/recalls/feed/", "kind": "fsn", "default": "美國"},
    {"url": "https://www.foodsafetynews.com/tag/salmonella/feed/", "kind": "fsn", "default": "美國"},
    {"url": "https://www.foodsafetynews.com/tag/listeria/feed/", "kind": "fsn", "default": "美國"},
    {"url": "https://www.foodsafetynews.com/tag/e-coli/feed/", "kind": "fsn", "default": "美國"},
    # Google News — 英文（gl=US，未偵測到他國時預設美國）
    {"url": "https://news.google.com/rss/search?q=food%20safety%20outbreak%20OR%20recall%20OR%20contamination%20when:365d&hl=en-US&gl=US&ceid=US:en",
     "kind": "gnews", "default": "美國"},
    {"url": "https://news.google.com/rss/search?q=salmonella%20OR%20listeria%20OR%20%22e.%20coli%22%20outbreak%20when:365d&hl=en-US&gl=US&ceid=US:en",
     "kind": "gnews", "default": "美國"},
    # Google News — 中文（台灣／華語圈）食安事件
    {"url": "https://news.google.com/rss/search?q=%E9%A3%9F%E5%93%81%E4%B8%AD%E6%AF%92%20OR%20%E9%A3%9F%E5%AE%89%20OR%20%E9%A3%9F%E5%93%81%E5%9B%9E%E6%94%B6%20OR%20%E9%A3%9F%E5%93%81%E4%B8%8B%E6%9E%B6%20when:365d&hl=zh-TW&gl=TW&ceid=TW:zh-Hant",
     "kind": "gnews", "default": "台灣"},
]

# 國家/地區推斷（含中英關鍵字；歐盟先於美國，避免 ECDC/EFSA 子字串誤判）
COUNTRY_PATTERNS = [
    (r"\bEU\b|Europe|European|\bECDC\b|\bEFSA\b|Germany|France|Italy|Spain|Netherlands|Belgium|Sweden|Denmark|Ireland|Poland|歐盟|歐洲|德國|法國|義大利|西班牙|荷蘭", "歐盟"),
    (r"\bU\.?S\.?\b|United States|America|\bFDA\b|\bUSDA\b|\bCDC\b|美國|加州|紐約", "美國"),
    (r"\bUK\b|United Kingdom|Britain|British|England|Scotland|Wales|\bFSA\b|英國", "英國"),
    (r"Canada|Canadian|CFIA|加拿大", "加拿大"),
    (r"Australia|Australian|FSANZ|New Zealand|澳洲|紐西蘭", "澳洲"),
    (r"Japan|Japanese|日本", "日本"),
    (r"Hong Kong|香港", "香港"),
    (r"Taiwan|Taiwanese|台灣|臺灣|台北|臺北|新北|桃園|台中|臺中|台南|臺南|高雄|新竹|彰化|宜蘭|花蓮|衛福部|食藥署|食藥署", "台灣"),
    (r"China|Chinese|中國|大陸|北京|上海|Korea|韓國|Vietnam|越南|Thailand|泰國|India|印度|Indonesia|印尼|Malaysia|馬來西亞|Singapore|新加坡|Philippines|菲律賓|"
     r"Pakistan|巴基斯坦|Bangladesh|孟加拉|Cambodia|柬埔寨|Myanmar|緬甸", "亞洲其他"),
    # 全球性／其他地區 → 國際（須在預設美國之前攔下，避免誤判）
    (r"\bWHO\b|World Health|\bFAO\b|United Nations|worldwide|globe|global(?:ly)?|multi-?country|multiple countries|several countries|cross-border|國際|全球|多國", "國際"),
    (r"Paraguay|Brazil|Brazilian|Mexico|Mexican|Argentina|Chile|Peru|Colombia|Africa|Nigeria|Kenya|Egypt|Cape Verde|Russia|Ukraine|Saudi|\bUAE\b|Dubai|Israel|Turkey|巴西|墨西哥|阿根廷|非洲|中東", "國際"),
]

HAZARD_PATTERNS = [
    (r"salmonell|沙門", "沙門氏菌"),
    (r"listeri|李斯特", "李斯特菌"),
    (r"e\.?\s*coli|escherichia|STEC|O157|\bHUS\b|大腸桿菌", "大腸桿菌"),
    (r"cyclospor|環孢", "環孢子蟲"),
    (r"bacillus cereus|cereulide|仙人掌桿菌", "仙人掌桿菌"),
    (r"botulism|clostridium|肉毒", "肉毒桿菌"),
    (r"norovirus|諾羅", "諾羅病毒"),
    (r"hepatitis a|A型肝炎", "A型肝炎"),
    (r"campylobacter|彎曲桿菌", "彎曲桿菌"),
    (r"cronobacter|阪崎", "阪崎腸桿菌"),
    (r"aflatoxin|mycotoxin|ochratoxin|黃[麴曲]|黴菌毒素", "黴菌毒素"),
    (r"undeclared|allergen|過敏原|致敏", "未標示過敏原"),
    (r"foreign (?:matter|material|object)|metal|plastic|glass|異物|玻璃|金屬碎片", "異物"),
    (r"塑化劑|重金屬|鉛|鎘|砷|超標", "化學污染物"),
    (r"recall|回收|下架|召回", "回收"),
    (r"outbreak|疫情|爆發|群聚", "疫情爆發"),
    (r"poisoning|illness|中毒|食物中毒|食品中毒", "食品中毒"),
]

# 標題尾巴：媒體常在具體事件標題後追加「導讀子句」或分類標籤，例如
#   「FDA Announces Recall on Cheese Over Listeria Outbreak: What to Know」
#   「桃園便當店疑食品中毒累計104人有症狀69人就醫| 地方」
# 這種要「剝掉尾巴」而不是整則丟掉，否則會誤殺真正的召回／疫情；
# 剝乾淨後同一則事件的不同版本標題也才對得起來（利於去重）。
TAIL_RE = re.compile(r"""
    (?:
        [.:\-–—|｜]\s*
        (?: what\ (?:to|you\ (?:need\ to|should))\ know .*
          | here.?s\ (?:what|how|why) .*
          | everything\ you\ need\ to\ know .*
          | explained
          )
      | [|｜]\s*(?:一次看懂?|懶人包|Q\s*&\s*A|QA)\s*
      | [|｜]\s*(?:要聞|生活|健康|醫療|社會|地方|財經|國際|政治|影音|即時|焦點
                  |大台北|桃竹苗|中彰投|雲嘉南|高屏|宜花東|北部|中部|南部|東部|全台)\s*
    )\s*$
""", re.I | re.X)


def strip_tail(title: str) -> str:
    """剝掉標題尾端的導讀子句／新聞分類標籤，回傳事件本體。"""
    t = (title or "").strip()
    for _ in range(3):  # 可能連掛兩層，例如「…| 沙拉油爆致癌物| 生活」
        new = TAIL_RE.sub("", t).strip(" -–—|｜:：、,，。.")
        if new == t or not new:
            break
        t = new
    return t


# 「非具體事件」雜訊：意見專欄、週期性追蹤欄、多主題彙整、年度回顧、
# 問答／衛教解釋文、統計彙整、政策修法與政治後續。
# 這些只是評論/新聞，沒有具體召回或疫情標的，使用者不需要（且常重複）
NOISE_RE = re.compile(r"""
    # --- 意見專欄／週期性追蹤欄／彙整／回顧 ---
      ^\s*publisher.?s\ platform        # 出版人意見專欄（Bill Marler）
    | ^\s*opinion\s*[|:]                 # 意見文章
    | ^\s*article\s*[-–—|]               # 轉載評論（Article - ...）
    | ^\s*quick\ takes\b                 # 多主題新聞彙整
    | investigation\ update\s*:          # 週期性追蹤專欄
    | where\ people\ got\ sick           # 週期性追蹤專欄
    | when\ people\ go[t]\ sick          # 週期性追蹤專欄（When People Got Sick）
    | when\ people\ get\ sick
    | year\ in\ review                   # 年度回顧
    | review\ includes                   # 年度回顧
    | letter\ from\ the\ editor

    # --- 問答／衛教／解釋文（已先剝尾巴，仍命中代表整篇就是解釋文）---
    | ^\s*q\s*&?\s*a\s*[:：]
    | what\ (?:to|you\ need\ to)\ know\b
    | what\ .{0,40}?\ need\ to\ know\b
    | here.?s\ (?:what|how|why)\b
    | answers\ to\ your\b
    | (?:most\ common|frequently\ asked)\ questions
    | \bexplain(?:s|ed|er)\b
    | ^\s*(?:can|should|is|are|do|does|why|how|what|when|who)\b[^?]{0,70}\?   # 問句式標題
    | \btips\ (?:for|to|on|amid)\b
    | food\ handling\ tips
    | \bhow\ to\ (?:avoid|stay|keep|protect)\b
    | \bwhat\ is\ cross.contamination\b

    # --- 反應／評論／專題／統計彙整（不是新事件）---
    | \b(?:respond|reacts?|reaction)s?\ to\ the\ (?:outbreak|recall)
    | \bin\ focus\s*[:：]
    | \bweigh(?:s|ed)?\ in\ on\b
    | recalls?\ (?:surged|spiked|jumped|rose|climbed)\b
    | \bby\ the\ numbers\b
    | \bare\ you\ recall.ready\b
    | ^\s*video\b                                   # 電視新聞影音片段
    | reveals?\ (?:holes|gaps|flaws|cracks|weaknesses|problems)
    | \bwhat\ .{0,50}\ reveals\ about\b
    | \bwhat\ .{0,40}\ are\ eating\b
    | \bsurvey\ (?:finds|shows|reveals)\b
    | \bgrowing\ concern\b
    | raises?\ (?:new\ )?(?:concerns|questions)\b
    | \band\ politics\b
    | \blessons\ (?:from|learned)\b
    | \bprompts?\ .{0,45}?\ to\ (?:rethink|reconsider)\b
    | \bweigh(?:s|ing)?\ .{0,25}?(?:concerns|options|risks)\b
    | \bhighlights?\ (?:value|importance|need)\ (?:of|for)\b
    | \bstress(?:es)?\ food\ safety\b
    | \brethink\ food\ safety\b

    # --- 週報／查核／民調／數據分析／政策與進口執法彙整（2026-09 使用者回報「很雜」後新增）---
    | \bsunday\ edition\b
    | \bfact.?check
    | \bpolls?\b
    | \b(?:analysis|data|study|studies|survey)\ (?:finds|shows?|reveals?|suggests?|highlights?)\b
    | \bscientists?\ (?:flag|reveal|warn|say)\w*\b
    | \btrends?\b
    | \bseeing\ a\ surge\b | \boutbreaks\ surge\b
    | \bsummer\ of\b
    | \bwhy\ (?:this|it)\ (?:has|feels|is)\b
    | \bsafety\ net\b
    | \b(?:federal|trump)\ (?:food\ safety\ )?cuts\b | \bcuts\ to\b
    | \bwhat.?s\ safe\ to\ eat\b
    | \bprecautions\b
    | \bfaqs?\b
    | ^\s*what\b.{0,60}\bshould\ know\b
    | \byou\ should\ know\ about\b
    | \bimport\ (?:enforcement|alerts?)\b
    | \bwarns?\ .{0,20}?importers?\b
""", re.I | re.X)

# 中文：政策／修法／政治後續／衛教宣導（非具體事件）
# 註：刻意不收「營養師／醫師」——會誤殺「高雄春捲爆67人食物中毒！營養師點名…」這類真事件
NOISE_ZH_RE = re.compile(
    r"修法|修正草案|草案|三讀|立法院|立委|議員|議會|質詢|公聽會|"
    r"食安會議|食安論壇|研商|座談會|說明會|研討會|"
    r"擬設|擬修|研議|專家建議|提\d+項建議|籲|呼籲|喊話|批評|抨擊|抱怨|"
    r"選戰|參選|政見|藍綠|朝野|攻防|"
    r"精進作為|加強宣導|宣導活動|"
    r"懶人包|一次看|怎麼辦|如何分辨|如何避免|教你|"
    r"社論|專欄"
)


def is_noise(title: str) -> bool:
    """意見／專欄／彙整／回顧／解釋文／政策後續等『非具體事件』新聞 → True 表示應濾除。

    供本爬蟲與 build_data 清理既有資料共用（自癒：舊雜訊下次跑也會被移除）。
    先剝掉尾巴再判斷，避免「真事件標題 + : What to Know」被整則誤殺。
    """
    t = strip_tail(title or "")
    return bool(NOISE_RE.search(t) or NOISE_ZH_RE.search(t))


# 同一場疫情的「人數又增加了」追蹤報導。大型疫情（如環孢子蟲）每天都會出一則，
# 但事件本身已經有一則了 → 只留最初那則，符合「一個事件一則」的原則。
COUNT_UPDATE_RE = re.compile(r"""
      \b(?:patient|case)\ count\b
    | \bcount\ .{0,30}?(?:grows|grow|increase|increases|rises|rise|climbs|continue)
    | \bmore\ (?:infections|cases|illnesses|people\ sick)\b
    | \b(?:cases|infections|illnesses|patients|victims)\ .{0,20}?
        (?:grows|grow|rises|rise|climbs|climb|increases|increase|tops|top|surpass\w*|jumps|jump)\b
    | \b(?:outbreak|toll)\ (?:grows|widens|continues\ to\ (?:grow|spread|increase))\b
    | \bnumber\ of\ (?:cases|patients|illnesses|people)\ .{0,15}?(?:grows|rises|climbs|increases)\b
    | \bcontinues\ to\ (?:increase|grow|rise|climb)\b
""", re.I | re.X)

# 有「新進展」就不算單純人數更新 —— 死亡、住院、召回（含擴大）、找到污染源都要留。
# 註：expand 也算 —— 「Swedish hepatitis A outbreak expands with 11 sick」這種是該疫情
# 唯一一則報導，濾掉整場疫情就從網站消失了。
ESCALATION_RE = re.compile(
    r"\b(?:death|deaths|dead|deadly|died|dies|fatal|fatality|killed|kills)\b"
    r"|\bhospitaliz\w*\b|\brecall\w*\b|\bexpand\w*\b"
    r"|\bnamed\ as\ source\b|\bsource\ (?:identified|confirmed|found)\b"
    r"|\bfirst\ (?:death|case)\b|\b1st\ death\b", re.I | re.X)


def is_count_update(title: str) -> bool:
    """純粹只是「人數又增加」的後續追蹤 → True 表示應濾除。

    刻意做得保守：只認明確的人數／案例數增長措辭，且標題不得帶有新進展。
    （曾試過用詞頻分群判斷「同一場疫情是否已有更早報導」，會把 expands、
    identified 這類動詞誤當成專指詞而亂配，反而有刪掉整場疫情的風險，故不採用。）
    """
    t = strip_tail(title or "")
    return bool(COUNT_UPDATE_RE.search(t)) and not ESCALATION_RE.search(t)


# 相關性過濾：標題須命中食安事件關鍵字（濾掉政策/活動/產業新聞等雜訊）
# 原本只套用在 Google News；Food Safety News 全收，結果混進「Labor Day…」「蘋果採收革新」
# 這類產業新聞 → 2026-09 起兩者都要過（build_data 也用它清理既有資料）
INCIDENT_KW = re.compile(
    r"outbreak|recall|salmonell|listeri|e\.?\s*coli|\bHUS\b|botulism|contamin|poison|illness|"
    r"hepatitis|norovirus|cyclospor|cereus|campylobacter|cronobacter|vibrio|parasite|"
    r"sicken|\bsick\b|\bdie[sd]?\b|death|hospitali|infection|"
    r"toxic|undeclared|allergen|\bwarning\b|"
    r"tainted|unsafe|adulterat|withdrawn|alert|"
    r"中毒|回收|下架|召回|污染|沙門|李斯特|大腸桿菌|肉毒|諾羅|黴菌|黃[麴曲]|"
    r"塑化劑|超標|不合格|黑心|過期|致癌|毒|異物|疫情|群聚", re.I)


def is_incident(title: str) -> bool:
    """標題看得出是具體食安事件（召回／疫情／中毒／污染）→ True。"""
    return bool(INCIDENT_KW.search(title or ""))


def incident_tags(title: str, summary: str = "") -> list[str]:
    """食安事件卡片的標籤：只放中文危害分類。

    以前還會塞媒體名（foodsafetynews.com、CBS News）、公司名（Taylor Farms）
    和 RSS 英文分類（outbreaks、Salmonella），造成同一概念中英各顯示一次、
    卡片上一堆不是分類的字 → 看起來很雜。來源媒體已寫在 AI 重點「來源：」那行。
    """
    return ["食安事件"] + _all_hazards(f"{title or ''} {(summary or '')[:300]}")


def _detect(patterns, text, default=None):
    for pat, label in patterns:
        if re.search(pat, text, re.I):
            return label
    return default


def country_from_title(title: str) -> str | None:
    """只看標題判斷國家；標題沒點名任何國家時回傳 None。

    爬蟲是用「標題＋RSS 分類＋內文摘要」判斷的，摘要常順帶提到 FDA、CDC，
    會把「Eggs blamed in Chinese Salmonella outbreak」誤判成美國；
    中文新聞沒點名國家時又一律預設台灣（例：印尼營養午餐中毒被標成台灣）。
    標題明講的國家最可靠 → build_data 清理時以它為準。
    """
    return _detect(COUNTRY_PATTERNS, title or "")


def _all_hazards(text):
    out = []
    for pat, label in HAZARD_PATTERNS:
        if re.search(pat, text, re.I) and label not in out:
            out.append(label)
    return out


# 去重用最短前綴長度：短於此的標題不做前綴比對，避免把不同事件併掉
DUP_MIN_PREFIX = 24


def _norm_title(t: str) -> str:
    """去重鍵：剝尾巴後只留英數與中日韓文字（標點、空白、大小寫差異都不算）。

    不再截斷長度 —— 改由 _same_event() 以「前綴包含」判斷，
    這樣「同一標題被追加子句」（Google News 常見）也能對上。
    """
    return re.sub(r"[^0-9a-z一-鿿぀-ヿ]+", "", strip_tail(t or "").lower())


def _same_event(a: str, b: str) -> bool:
    """兩個正規化標題是否指同一則事件：完全相同，或一方是另一方的前綴。"""
    if a == b:
        return True
    short, long = (a, b) if len(a) <= len(b) else (b, a)
    return len(short) >= DUP_MIN_PREFIX and long.startswith(short)


# ---------- 同一事件歸併：只「摺疊」不刪除 ----------
# 大型事件（辣椒沙門氏菌、中聯油品、Clover Hill 起司）每天會有十幾家媒體各寫一則，
# 標題都不一樣，靠標題去重對不起來，網站上就一整排同一件事。
# 這裡替同一事件的報導標上同一個 event_id，前端摺成一張卡（最新一則當主卡，
# 其餘收在「同一事件另有 N 則報導」）。因為只是摺疊、原報導都還點得到，
# 萬一誤判也不會讓任何事件從網站上消失 —— 這是跟以前「用詞頻判斷後刪除」最大的差別。
EVENT_WINDOW_DAYS = 21  # 與該事件最新報導相差超過三週 → 視為另一波，另起一張卡

EVENT_PATHOGENS = [
    (r"salmonell|沙門", "sal"), (r"listeri|李斯特", "lis"),
    (r"e\.?\s*coli|STEC|\bO1\d\d\b|\bHUS\b|大腸桿菌", "eco"), (r"cyclospor|環孢", "cyc"),
    (r"botul|肉毒", "bot"), (r"norovirus|諾羅", "nor"), (r"hepatitis a|A型肝炎", "hep"),
    (r"campylobacter|彎曲桿菌", "cam"), (r"cereus|cereulide|仙人掌桿菌", "bce"),
    (r"aflatoxin|黃[麴曲]", "afl"), (r"苯駢芘|苯并芘|benzo", "bap"),
]

# 英文：不能用來判斷「同一事件」的泛用字（事件動詞、機構、數量、時間、通路名……）
# 通路名（Walmart、Costco…）特別列入：同一家賣場一個月內常有好幾起不相干的召回
_EVENT_STOP_WORDS = """
outbreak outbreaks recall recalls recalled recalling salmonella listeria coli cyclospora cyclosporiasis
linked link links traced tied trace sick sickens sickened illness illnesses patient patients case cases
people person states state multistate investigation investigating investigate officials official public
health update updates new more than after amid over because contamination contaminated potential risk
risks possible from with into this that year years about report reported reports reporting confirmed
announces announced issues issued issue food foods product products company companies says said warns
warning alert alerts expands expanded expand grows growing increases number count hospitalized
hospitalizations death deaths dies died dead fatal deadly fda cdc usda fsis federal nationwide
monocytogenes shiga toxin producing o157 o145 h28 declared ends closed close probe source unknown still
ongoing another added includes include now under least nearly almost around some other their they have
been were will could first second third days weeks week month months january february march april june
july august september october november december 2024 2025 2026 infections infection infected ill hospital
strain brand brands sold stores store retailers retailer what know here top tops most largest record
massive big major dozens hundreds thousands several family families consumer consumers safety safe
lack pieces spreads spread rising rise double normal experts expert importers importer import imported
enforcement cuts local county city officials sickening kills killed lawsuit suing sues filed
farm farms tainted pull pulls pulled
walmart costco kroger target publix aldi lidl trader joe whole hannaford h-e-b
""".split()
EVENT_STOP = {w.rstrip("s") for w in _EVENT_STOP_WORDS}

# 中文：常見但沒有鑑別力的雙字詞
EVENT_STOP_ZH = set("""
食品 品中 中毒 食物 物中 疑似 衛生 生局 集體 回收 下架 召回 爆發 疫情 案件 事件 食安 人疑 就醫 送醫
腹瀉 嘔吐 稽查 查獲 抽驗 不合 合格 超標 產品 業者 衛福 福部 食藥 藥署 發聲 聲了 回應 應了 公布 持續
追查 民眾 消費 費者 注意 最新 今天 昨天 日前 市府 縣府 政府 局長 表示 指出 相關
""".split())


def _event_sig(item: dict):
    """算出一則報導的事件特徵；沒有日期的回傳 None（不參與歸併）。"""
    from datetime import date as _date
    try:
        d = _date.fromisoformat((item.get("date") or "")[:10])
    except ValueError:
        return None
    t = item.get("title") or ""
    en = {w.rstrip("s") for w in re.findall(r"[a-z][a-z'\-]{3,}", t.lower())} - EVENT_STOP
    cjk = "".join(re.findall(r"[一-鿿]+", t))
    zh = {cjk[i:i + 2] for i in range(len(cjk) - 1)} - EVENT_STOP_ZH
    blob = t + " " + (item.get("summary") or "")[:200]
    pathogens = {k for pat, k in EVENT_PATHOGENS if re.search(pat, blob, re.I)}
    return {"d": d, "en": en, "zh": zh, "p": pathogens, "poi": "中毒" in t,
            "c": item.get("country"), "url": item.get("url")}


# 罕見危害：同一國家三週內幾乎都是同一場事件（環孢子蟲疫情、苯駢芘油品案），
# 不必再比對專指詞。沙門氏菌／李斯特菌等常見病原同時會有好幾場，不能這樣認。
RARE_EVENT_PATHOGENS = {"cyc", "bap"}


def _event_match(a: dict, b: dict) -> bool:
    """兩則報導是否在講同一事件（保守：同國家、病原不衝突、且有足夠的專指詞重疊）。"""
    if a["c"] != b["c"]:
        return False
    if a["p"] and b["p"] and not (a["p"] & b["p"]):
        return False
    shared_p = a["p"] & b["p"]
    if shared_p & RARE_EVENT_PATHOGENS:
        return True
    shared_en = a["en"] & b["en"]
    shared_zh = a["zh"] & b["zh"]
    if len(shared_zh) >= 2 or len(shared_en) >= 2:
        return True
    if not (shared_p or (a["poi"] and b["poi"])):
        return False
    if shared_en:
        return True
    # 中文只共用一個專指詞（「成淵」高中／「成淵」國中部）→ 同為中毒／同病原且五天內才算
    return bool(shared_zh) and abs((a["d"] - b["d"]).days) <= 5


def assign_events(items: list[dict]) -> int:
    """替同一事件的報導設定相同的 item['event_id']（= 該事件最新一則的 URL）。

    每次都從頭重算（自癒）。回傳被摺疊進其他卡片的報導數。
    新報導要加入某事件，必須跟該事件的主報導（最新一則）相符，或跟其中兩則以上相符
    —— 避免 A 像 B、B 像 C 一路串下去，把不同事件串成一大串。
    """
    for it in items:
        it.pop("event_id", None)
    dated = [(s, it) for it in items if (s := _event_sig(it))]
    dated.sort(key=lambda x: (x[0]["d"], x[1].get("first_seen") or ""), reverse=True)

    active: list[list] = []   # 每群：[(sig, item), ...]，第 0 則是主報導
    done: list[list] = []
    for sig, it in dated:
        # 主報導比這則新超過三週的群，之後只會更舊，永遠不會再配到 → 收掉
        still = []
        for grp in active:
            (done if (grp[0][0]["d"] - sig["d"]).days > EVENT_WINDOW_DAYS else still).append(grp)
        active = still
        home = None
        for grp in active:
            if _event_match(sig, grp[0][0]) or sum(_event_match(sig, s) for s, _ in grp) >= 2:
                home = grp
                break
        if home is None:
            active.append([(sig, it)])
        else:
            home.append((sig, it))

    folded = 0
    for grp in done + active:
        if len(grp) < 2:
            continue
        eid = grp[0][0]["url"]
        for _, it in grp:
            it["event_id"] = eid
        folded += len(grp) - 1
    return folded


def crawl() -> list[dict]:
    items: list[dict] = []
    seen_urls: set[str] = set()
    seen_titles: set[str] = set()

    for feed in FEEDS:
        try:
            root = ET.fromstring(fetch(feed["url"], timeout=20))
        except Exception as e:
            print(f"  [食安事件] 略過一個來源: {str(e)[:50]}")
            continue

        for node in root.findall(".//item"):
            link = (node.findtext("link") or "").strip()
            raw_title = clean_text(node.findtext("title") or "")
            if not link or not raw_title:
                continue

            # Google News 標題尾端常帶「 - 媒體名」，且來源在 <source>
            outlet = clean_text(node.findtext("source") or "")
            title = raw_title
            if feed["kind"] == "gnews" and outlet and title.endswith(outlet):
                title = title[: -len(outlet)].rstrip(" -–—|").strip()
            elif feed["kind"] == "gnews":
                title = re.sub(r"\s[-–—]\s[^-–—]{2,30}$", "", title).strip()

            # 剝掉導讀子句／新聞分類標籤，留下事件本體
            title = strip_tail(title) or title

            # 相關性過濾（Google News 與 Food Safety News 都要過）
            if not is_incident(raw_title):
                continue

            # 濾掉意見專欄／解釋文／彙整／政策後續（非具體事件）
            if is_noise(raw_title) or is_noise(title):
                continue

            # 濾掉同一場疫情的「人數又增加」後續追蹤
            if is_count_update(title):
                continue

            nt = _norm_title(title)
            if link in seen_urls or (nt and any(_same_event(nt, s) for s in seen_titles)):
                continue
            seen_urls.add(link)
            if nt:
                seen_titles.add(nt)

            date = normalize_date(node.findtext("pubDate") or "")
            cats = [c.text or "" for c in node.findall("category")]
            desc = clean_text(re.sub(r"<[^>]+>", " ", node.findtext("description") or ""))[:300]

            blob = title + " " + " ".join(cats) + " " + desc
            country = _detect(COUNTRY_PATTERNS, blob, default=feed["default"])
            hazards = _all_hazards(blob)

            # 只放中文危害分類（媒體名／公司名／英文 RSS 分類不當標籤，見 incident_tags）
            tags = ["食安事件"] + hazards

            src_name = outlet or ("Food Safety News" if feed["kind"] == "fsn" else "新聞")
            ai = [f"性質：食安事件 — {country}"]
            if hazards:
                ai.append("病原／危害：" + "、".join(hazards[:4]))
            ai.append(f"事件：{title[:100]}")
            if date:
                ai.append(f"日期：{date}")
            ai.append(f"來源：{src_name}（新聞報導）")

            item = make_item(
                source="food_incidents",
                source_label="食安事件",
                source_color="red",
                title=title,
                url=link,
                date=date,
                summary=(desc or title)[:500],
                tags=tags,
            )
            item["country"] = country
            item["ai_summary"] = ai
            items.append(item)

    print(f"  [食安事件] 全球食安新聞 + 各國新聞事件 {len(items)} 筆")
    return items


if __name__ == "__main__":
    import json
    from collections import Counter
    out = crawl()
    print("國家:", dict(Counter(i["country"] for i in out)))
    print(json.dumps(out[:3], ensure_ascii=False, indent=2))
