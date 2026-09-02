// 09-liff.js — LINE LIFF：SDK 初始化，以及 LINE WebView 存不了圖的補救
// 本站是純靜態課表，不讀任何會員資料，所以不呼叫 liff.login()／liff.getProfile()，
// 也不設 withLoginOnExternalBrowser — 用一般瀏覽器開這頁時完全不會被導去登入。
var LIFF_ID = window.LIFF_ID || '';
function inLINE(){
  return document.documentElement.classList.contains('liff');
}
// SDK 只在 LINE 裡才載入：在外面開這頁不會多打一次 LINE 的網路
(function(){
  if (!inLINE() || !LIFF_ID) return;
  var s = document.createElement('script');
  s.src = 'https://static.line-scdn.net/liff/edge/2/sdk.js';
  s.onload = function(){
    liff.init({liffId: LIFF_ID}).catch(function(e){
      // init 失敗不影響課表本身，頁面照樣能看
      console.warn('liff.init failed:', e);
    });
  };
  document.head.appendChild(s);
})();

// LINE 的 WebView 會擋掉 <a download>（iOS 尤其直接沒反應），
// 所以在 LINE 裡改成把圖片攤在全螢幕，讓使用者長按存到相簿
function saveImage(url, name){
  if (!inLINE()) {
    var a = document.createElement('a');
    a.download = name;
    a.href = url;
    a.click();
    return;
  }
  var en = document.getElementById('sheet').classList.contains('en');
  var tip = en ? 'Press and hold the image to save it' : '長按圖片即可儲存到相簿';
  var box = document.createElement('div');
  box.className = 'shot';
  box.setAttribute('data-noexport', '1');
  box.setAttribute('role', 'dialog');
  box.setAttribute('aria-modal', 'true');
  box.setAttribute('aria-label', tip);
  var bar = document.createElement('div');
  bar.className = 'shot-bar';
  bar.appendChild(document.createTextNode(tip));
  var x = document.createElement('button');
  x.className = 'shot-x';
  x.type = 'button';
  x.setAttribute('aria-label', en ? 'Close' : '關閉');
  x.textContent = '✕';
  bar.appendChild(x);
  var body = document.createElement('div');
  body.className = 'shot-body';
  var img = document.createElement('img');
  img.src = url;
  img.alt = name;
  body.appendChild(img);
  box.appendChild(bar);
  box.appendChild(body);
  function close(){
    box.remove();
    document.removeEventListener('keydown', esc);
  }
  function esc(e){ if (e.key === 'Escape') close(); }
  x.addEventListener('click', close);
  document.addEventListener('keydown', esc);
  document.body.appendChild(box);
  x.focus();
}
