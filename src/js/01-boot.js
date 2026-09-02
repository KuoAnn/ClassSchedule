// 01-boot.js — 在畫面繪製前決定版型與 viewport，避免閃動；必須最先執行
// 這支跟其他 JS 不在同一個 <script>，所以 setViewport 用全域函式讓 05-view.js 呼叫得到
function setViewport(narrow){
  var m = document.querySelector('meta[name=viewport]');
  if (!m) return;
  // 寬版是固定寬度的海報版面，交給瀏覽器整頁縮放（不給 initial-scale）；
  // 窄版才跟著裝置寬度走，這樣 LINE LIFF 裡的字級才會是正常大小
  var w = parseInt(getComputedStyle(document.documentElement)
    .getPropertyValue('--sheetw'), 10) || 2040;
  m.setAttribute('content', narrow
    ? 'width=device-width,initial-scale=1,viewport-fit=cover'
    : 'width=' + w + ',viewport-fit=cover');
}
(function(){
  // LINE 內建瀏覽器（含 LIFF）的 UA 一定帶 " Line/"；先掛 .liff 讓 CSS 在繪製前就到位
  var inline = / Line\//i.test(navigator.userAgent || '');
  var v;
  try { v = localStorage.getItem('yoga-view'); } catch(e) {}
  // LIFF 一律先給窄版：手機螢幕塞不下寬版格線
  if (v !== 'n' && v !== 'w') v = (inline || (window.innerWidth || 1200) < 900) ? 'n' : 'w';
  document.documentElement.className = (v === 'n' ? 'nv' : 'wv') + (inline ? ' liff' : '');
  setViewport(v === 'n');
})();
