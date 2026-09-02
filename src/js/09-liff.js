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

// 把「現在看到的這一版」寫成網址參數：版型與語言要帶，否則外部瀏覽器會用它自己
// 記住的偏好，存出來的圖跟 LINE 裡看到的不一樣。**篩選不帶** —— 下載的是完整課表，
// 帶過去只會讓外部瀏覽器那邊多套一次又被 08-export.js 解掉，白跑一趟。
// 只取 origin + pathname：LIFF 進來時網址可能還掛著 liff.state 之類的參數
function exportUrl(){
  var q = ['dl=1', 'v=' + (document.documentElement.classList.contains('nv') ? 'n' : 'w'),
           'l=' + (document.getElementById('sheet').classList.contains('en') ? 'en' : 'zh')];
  return location.origin + location.pathname + '?' + q.join('&');
}

// 在 LIFF 裡存圖一律丟給外部瀏覽器：LINE 的 WebView 存不了檔，
// 外面才有正常的「下載」。回傳 true 表示已接手，08-export.js 就不用在 WebView
// 裡先畫一次 canvas（手機畫這張很慢，畫完也用不到）。
// 只有 liff.isInClient() 為真才算數：從聊天室點一般連結進來的是 LINE 內建瀏覽器，
// 那裡 openWindow 只會在 LINE 自己開新分頁，等於沒解決問題，得走長按那條路。
function openExternalDownload(){
  if (!inLINE() || !liffReady || !window.liff || !liff.openWindow) return false;
  if (!liff.isInClient || !liff.isInClient()) return false;
  try {
    liff.openWindow({url: exportUrl(), external: true});
  } catch(e) {
    console.warn('liff.openWindow failed:', e);
    return false;
  }
  var live = document.getElementById('live');
  if (live) {
    live.textContent = document.getElementById('sheet').classList.contains('en')
      ? 'Opening the browser to download the image'
      : '已開啟瀏覽器下載圖片';
  }
  return true;
}

// 走到這裡的 LINE 使用者是沒有 LIFF SDK 的（沒設 LIFF_ID／init 失敗／LINE 內建瀏覽器），
// <a download> 在那裡會直接沒反應，所以把圖片攤在全螢幕讓使用者長按存到相簿
function saveImage(url, name){
  if (!inLINE()) {
    var a = document.createElement('a');
    a.download = name;
    a.href = url;
    a.click();
    // blob 要等瀏覽器真的把檔案抓完才能收，立刻 revoke 會下載到空檔
    if (url.indexOf('blob:') === 0) {
      setTimeout(function(){ URL.revokeObjectURL(url); }, 60000);
    }
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

// 外部瀏覽器被 openExternalDownload() 開起來時（?dl=1）：先把 LINE 裡的狀態套回來，
// 再自動按一次下載。版型已由 01-boot.js 依 ?v= 決定，這裡只補語言與篩選。
// 在 LINE 裡不自動觸發（例如有人把這個網址貼回聊天室），否則等於一進來就又要開瀏覽器
(function(){
  if (qparam('dl') !== '1' || inLINE()) return;
  var cat = qparam('cat');
  if (qparam('l') === 'en') applyLang('en');
  if (cat) { picked = cat; applyFilter(); }
  (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve())
    .then(function(){
      fitCells();
      syncRows();
      layout();
      // 量完版面再按，否則小時列還沒對齊，匯出的高度會是錯的
      requestAnimationFrame(function(){
        document.getElementById('dl').click();
        // 參數用完就從網址拿掉：重新整理這頁不該又下載一次
        if (history.replaceState) {
          history.replaceState(null, '', location.origin + location.pathname);
        }
      });
    });
})();
