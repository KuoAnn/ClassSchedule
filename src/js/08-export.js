// 08-export.js — 匯出 PNG（html2canvas）
document.getElementById('dl').addEventListener('click', function(){
  var btn=this, sheet=document.getElementById('sheet');
  var PNG = (window.SCHEDULE && window.SCHEDULE.png) || {zh:'schedule.png', en:'schedule.png'};
  btn.disabled=true; btn.classList.add('busy'); btn.setAttribute('aria-busy','true');
  var hide=sheet.querySelectorAll('[data-noexport]');
  (document.fonts&&document.fonts.ready?document.fonts.ready:Promise.resolve()).then(function(){
    fitCells();
    var nar = document.documentElement.classList.contains('nv');
    sheet.classList.add('nopast','flat','noto');
    document.querySelectorAll('.stt').forEach(function(c){ c.remove(); });
    document.querySelectorAll('.st-done,.st-live').forEach(function(c){
      c.classList.remove('st-done','st-live');
    });
    if (nar && !track.classList.contains('full')) sheet.classList.add('weekexp');
    hide.forEach(function(el){el.style.visibility='hidden'});
    // 手機 WebView 的 canvas 上限比桌機低，畫素太多會整個失敗；桌機仍維持 scale 2
    var area = sheet.offsetWidth * sheet.offsetHeight;
    var scale = (inLINE() || window.innerWidth < 900)
      ? Math.max(1, Math.min(2, Math.sqrt(12e6 / area))) : 2;
    return html2canvas(sheet,{scale:scale,backgroundColor:'#F4F0E9',useCORS:true,
      width:sheet.offsetWidth,height:sheet.offsetHeight,windowWidth:sheet.offsetWidth});
  }).then(function(canvas){
    hide.forEach(function(el){el.style.visibility=''});
    sheet.classList.remove('nopast','flat','noto','weekexp');
    markPast();
    var en = sheet.classList.contains('en');
    var nv = document.documentElement.classList.contains('nv');
    var name = (en ? PNG.en : PNG.zh)
      .replace('.png', (nv ? (en ? '-vertical' : '-直式') : '') + '.png');
    saveImage(canvas.toDataURL('image/png'), name);
    btn.disabled=false; btn.classList.remove('busy'); btn.removeAttribute('aria-busy');
  }).catch(function(e){
    hide.forEach(function(el){el.style.visibility=''});
    sheet.classList.remove('nopast','flat','noto','weekexp');
    markPast();
    btn.disabled=false; btn.classList.remove('busy'); btn.removeAttribute('aria-busy');
    alert('Export failed: '+e);
  });
});
