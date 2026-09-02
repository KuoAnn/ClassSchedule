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
    return html2canvas(sheet,{scale:2,backgroundColor:'#F4F0E9',useCORS:true,
      width:sheet.offsetWidth,height:sheet.offsetHeight,windowWidth:sheet.offsetWidth});
  }).then(function(canvas){
    hide.forEach(function(el){el.style.visibility=''});
    sheet.classList.remove('nopast','flat','noto','weekexp');
    markPast();
    var a=document.createElement('a');
    var en = sheet.classList.contains('en');
    var nv = document.documentElement.classList.contains('nv');
    a.download = (en ? PNG.en : PNG.zh)
      .replace('.png', (nv ? (en ? '-vertical' : '-直式') : '') + '.png');
    a.href=canvas.toDataURL('image/png'); a.click();
    btn.disabled=false; btn.classList.remove('busy'); btn.removeAttribute('aria-busy');
  }).catch(function(e){
    hide.forEach(function(el){el.style.visibility=''});
    sheet.classList.remove('nopast','flat','noto','weekexp');
    markPast();
    btn.disabled=false; btn.classList.remove('busy'); btn.removeAttribute('aria-busy');
    alert('Export failed: '+e);
  });
});
