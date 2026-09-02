// 01-boot.js — 在畫面繪製前決定版型與 viewport，避免閃動；必須最先執行
// 這支跟其他 JS 不在同一個 <script>，所以 setViewport 用全域函式讓 05-view.js 呼叫得到

// 裝置寬（CSS px）：HTML 裡的初始 viewport 是 device-width，所以「繪製前的這一刻」
// 量到的就是裝置寬。寬版把 viewport 換成固定寬之後就再也量不到了（clientWidth 會變成版面寬），
// 所以要先記下來 —— 寬版的 initial-scale 是拿它算的
var DEVW = document.documentElement.clientWidth || 0;
function setViewport(narrow){
  var m = document.querySelector('meta[name=viewport]');
  if (!m) return;
  // 寬版是固定寬度的海報版面：整頁縮到裝置寬。
  // 這裡把縮放比例明寫成 initial-scale，不再只靠瀏覽器自己 auto-shrink ——
  // LINE 的 WebView 對「切換後才改的 viewport」常常只吃寬度、不重算縮放，
  // 結果就是寬版超出螢幕、要橫向拖才看得完。量不到裝置寬時才退回原本的行為（不給 initial-scale）。
  var w = parseInt(getComputedStyle(document.documentElement)
    .getPropertyValue('--sheetw'), 10) || 2040;
  var c;
  if (narrow) {
    c = 'width=device-width,initial-scale=1,viewport-fit=cover';
  } else {
    c = 'width=' + w + (DEVW ? ',initial-scale=' + (DEVW / w).toFixed(4) : '')
      + ',viewport-fit=cover';
  }
  if (m.getAttribute('content') === c) return;
  // 整顆 meta 換掉，不是改 content：WebView（LINE／iOS）對屬性變更有時直接不重新套用
  var n = document.createElement('meta');
  n.setAttribute('name', 'viewport');
  n.setAttribute('content', c);
  m.parentNode.replaceChild(n, m);
}
// 轉向之後裝置寬變了，但寬版的 viewport 是固定寬、量不到新的值；
// 先退回 device-width 量一次，下一格再把寬版套回去（只在手機才需要，桌機不吃 viewport）
function remeasureViewport(){
  var de = document.documentElement;
  if (de.classList.contains('nv')) { DEVW = de.clientWidth || DEVW; return; }
  if (!de.classList.contains('liff') && window.innerWidth > 900) return;
  var m = document.querySelector('meta[name=viewport]');
  if (!m) return;
  m.setAttribute('content', 'width=device-width,initial-scale=1,viewport-fit=cover');
  requestAnimationFrame(function(){
    DEVW = de.clientWidth || DEVW;
    setViewport(false);
  });
}
window.addEventListener('orientationchange', remeasureViewport);
window.addEventListener('resize', function(){
  if (document.documentElement.classList.contains('nv')) DEVW = document.documentElement.clientWidth || DEVW;
});
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
  setViewport(v === 'n');
})();
