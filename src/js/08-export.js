// 08-export.js — 匯出 PNG（html2canvas）
// PNG 的 URL：blob 優先，data URL 只當退路 —— 手機瀏覽器對幾 MB 的 data URL
// 常常直接不下載（iOS Safari 尤其），而外部瀏覽器下載正是主要路徑
function pngUrl(canvas, cb){
  if (canvas.toBlob && window.URL && URL.createObjectURL) {
    canvas.toBlob(function(b){
      cb(b ? URL.createObjectURL(b) : canvas.toDataURL('image/png'));
    }, 'image/png');
    return;
  }
  cb(canvas.toDataURL('image/png'));
}
document.getElementById('dl').addEventListener('click', function(){
  var btn=this, sheet=document.getElementById('sheet');
  // 在 LIFF 裡直接把同一份課表交給外部瀏覽器下載，不必先在 WebView 畫一次
  // （手機畫這張很慢，而且 LINE 的 WebView 存不了檔，畫完也用不到）
  if (openExternalDownload()) return;
  var PNG = (window.SCHEDULE && window.SCHEDULE.png) || {zh:'schedule.png', en:'schedule.png'};
  btn.disabled=true; btn.classList.add('busy'); btn.setAttribute('aria-busy','true');
  var hide=sheet.querySelectorAll('[data-noexport]');
  function restore(){
    hide.forEach(function(el){el.style.visibility=''});
    sheet.classList.remove('nopast','flat','noto','weekexp','npack');
    markPast();
    btn.disabled=false; btn.classList.remove('busy'); btn.removeAttribute('aria-busy');
  }
  (document.fonts&&document.fonts.ready?document.fonts.ready:Promise.resolve()).then(function(){
    fitCells();
    var nar = document.documentElement.classList.contains('nv');
    sheet.classList.add('nopast','flat','noto');
    document.querySelectorAll('.stt').forEach(function(c){ c.remove(); });
    document.querySelectorAll('.st-done,.st-live').forEach(function(c){
      c.classList.remove('st-done','st-live');
    });
    // 直式匯出：空堂不留白，每天各自把卡片往上收（畫面上的小時列對齊只為了滑動時好比較）
    if (nar) sheet.classList.add('npack');
    if (nar && !track.classList.contains('full')) sheet.classList.add('weekexp');
    hide.forEach(function(el){el.style.visibility='hidden'});
    // 手機 WebView 的 canvas 上限比桌機低，畫素太多會整個失敗；桌機仍維持 scale 2
    var area = sheet.offsetWidth * sheet.offsetHeight;
    var scale = (inLINE() || window.innerWidth < 900)
      ? Math.max(1, Math.min(2, Math.sqrt(12e6 / area))) : 2;
    return html2canvas(sheet,{scale:scale,backgroundColor:'#F4F0E9',useCORS:true,
      width:sheet.offsetWidth,height:sheet.offsetHeight,windowWidth:sheet.offsetWidth});
  }).then(function(canvas){
    var en = sheet.classList.contains('en');
    var nv = document.documentElement.classList.contains('nv');
    restore();
    var name = (en ? PNG.en : PNG.zh)
      .replace('.png', (nv ? (en ? '-vertical' : '-直式') : '') + '.png');
    pngUrl(canvas, function(url){ saveImage(url, name); });
  }).catch(function(e){
    restore();
    alert('Export failed: '+e);
  });
});
