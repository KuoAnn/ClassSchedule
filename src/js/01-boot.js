// 01-boot.js — 在畫面繪製前決定版型，避免閃動；必須最先執行
// 這支跟其他 JS 不在同一個 <script>，所以 qparam() 用全域函式讓後面的檔案呼叫得到

// viewport 兩種版型共用一份（`width=device-width,initial-scale=1`，寫在 src/index.html）。
// 寬版曾經在切過去時把 viewport 換成 `width=<--sheetw>` 並自己算 initial-scale，
// 想讓整張海報一眼看完；但 2040px 的海報縮到手機寬只有 0.19 倍，16px 的課名剩 3px，
// 而且 viewport 變成 2040 之後 `@media (max-width:900px/560px)` 全部不再成立 ——
// 標題列、按鈕、色票列在手機上照桌機尺寸出，整個寬版等於沒有 RWD。
// 現在寬版改成「原尺寸＋橫向捲動」：字級是原尺寸、chrome 吃得到 media query，
// 想看全貌的人雙指縮小就是以前的樣子（沒有設 maximum-scale／user-scalable）。
// 想改回「整頁縮到裝置寬」之前先看 AGENTS.md 的「LIFF：五條約束」第 1 條。

// 網址參數用小工具：?v=n 這種分享連結要在繪製前就決定版型，所以放在 01-boot.js
function qparam(k){
  var m = new RegExp('[?&]' + k + '=([^&]*)').exec(location.search || '');
  return m ? decodeURIComponent(m[1].replace(/\+/g, ' ')) : '';
}
(function(){
  // LINE 內建瀏覽器（含 LIFF）的 UA 一定帶 " Line/"；先掛 .liff 讓 CSS 在繪製前就到位
  var inline = / Line\//i.test(navigator.userAgent || '');
  // 網址指定的版型優先於記住的選擇：外部瀏覽器要重現的是 LINE 裡當下那一版
  var v = qparam('v');
  if (v !== 'n' && v !== 'w') {
    try { v = localStorage.getItem('yoga-view'); } catch(e) {}
  }
  // LIFF 一律先給窄版：手機螢幕塞不下寬版格線
  if (v !== 'n' && v !== 'w') v = (inline || (window.innerWidth || 1200) < 900) ? 'n' : 'w';
  document.documentElement.className = (v === 'n' ? 'nv' : 'wv') + (inline ? ' liff' : '');
})();
