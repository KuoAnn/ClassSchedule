// 08-export.js — 下載課表圖片
// 圖是 build 時就畫好的四張（scripts/shots.py：寬／窄 × 中／英），跟 HTML 放在同一層，
// 檔名由 build.py 寫進 window.SCHEDULE.png。按下載＝導到那個網址，瀏覽器直接顯示圖片，
// 手機長按、桌機右鍵就能存。
// 不再用 html2canvas 現畫：手機畫一次要好幾秒、canvas 有畫素上限會整個失敗，
// 而且 LINE 的 WebView 存不了 blob，等於畫完也用不到。
function shotUrl(){
  var v = document.documentElement.classList.contains('nv') ? 'n' : 'w';
  var l = document.getElementById('sheet').classList.contains('en') ? 'en' : 'zh';
  var m = (window.SCHEDULE && window.SCHEDULE.png) || {};
  var name = (m[v] || {})[l];
  if (!name) return '';
  // 圖跟 HTML 同一層；檔名有中文，要 encode 才貼得回網址
  return location.href.replace(/[?#].*$/, '').replace(/[^/]*$/, '')
    + encodeURIComponent(name);
}
document.getElementById('dl').addEventListener('click', function(){
  var url = shotUrl();
  if (!url) return;
  // LINE 的 WebView 顯示圖片時沒有「儲存」，所以先問 09-liff.js 要不要丟給外部瀏覽器
  if (openExternalDownload(url)) return;
  window.open(url, '_blank', 'noopener');
});
