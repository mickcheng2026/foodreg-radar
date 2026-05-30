/** Tailwind 設定 — 掃描 index.html 內用到的 class（含 JS 字串）產生最小化 CSS。
 *  重新編譯指令見 README「Tailwind 樣式」段落。 */
module.exports = {
  content: ["./index.html"],
  theme: { extend: {} },
  // 動態組出的顏色 class（在 JS 物件裡）以 safelist 保底，確保不被 tree-shake 掉
  safelist: [
    {
      pattern:
        /(bg|text|border)-(emerald|amber|indigo|blue|purple|rose|cyan|yellow|lime|slate|red|orange|teal)-(50|100|200|300|500|600|700)/,
    },
  ],
  plugins: [],
};
