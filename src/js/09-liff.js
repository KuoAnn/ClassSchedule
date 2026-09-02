// 09-liff.js — LINE LIFF：SDK 初始化，以及 LINE WebView 存不了圖的補救
// 本站是純靜態課表，不讀任何會員資料，所以不呼叫 liff.login()／liff.getProfile()，
// 也不設 withLoginOnExternalBrowser — 用一般瀏覽器開這頁時完全不會被導去登入。
var LIFF_ID = window.LIFF_ID || '';
var liffReady = false;
function inLINE(){
  return document.documentElement.classList.contains('liff');
}
// SDK 只在 LINE 裡才載入：在外面開這頁不會多打一次 LINE 的網路
(function(){
  if (!inLINE() || !LIFF_ID) return;
  var s = document.createElement('script');
  s.src = 'https://static.line-scdn.net/liff/edge/2/sdk.js';
  s.onload = function(){
    liff.init({liffId: LIFF_ID}).then(function(){
      liffReady = true;
    }).catch(function(e){
      // init 失敗不影響課表本身，頁面照樣能看（存圖退回長按那條路）
      console.warn('liff.init failed:', e);
    });
  };
  document.head.appendChild(s);
})();

// 在 LIFF 裡看圖一律丟給外部瀏覽器：LINE 的 WebView 顯示圖片時沒有「儲存」，
// 外面才有正常的長按選單與下載。回傳 true 表示已接手，08-export.js 就不再自己開。
// 圖是 build 時畫好的，所以這裡傳的是圖片的固定網址 —— 以前沒有圖可以傳，
// 只能用 ?dl=1&v=…&l=… 把整份課表在外部瀏覽器重現一次再畫，那條路整段拿掉了。
// 只有 liff.isInClient() 為真才算數：從聊天室點一般連結進來的是 LINE 內建瀏覽器，
// 那裡 openWindow 只會在 LINE 自己開新分頁，等於沒解決問題。
function openExternalDownload(url){
  if (!inLINE() || !liffReady || !window.liff || !liff.openWindow) return false;
  if (!liff.isInClient || !liff.isInClient()) return false;
  try {
    liff.openWindow({url: url, external: true});
  } catch(e) {
    console.warn('liff.openWindow failed:', e);
    return false;
  }
  var live = document.getElementById('live');
  if (live) {
    live.textContent = document.getElementById('sheet').classList.contains('en')
      ? 'Opening the image in your browser'
      : '已開啟瀏覽器顯示圖片';
  }
  return true;
}

