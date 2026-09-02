// 04-narrow.js — 窄版輪播：無限循環、當日置中、小時列對齊、釘住的星期
var track = document.getElementById('ntrack'), cur = 0;
var navp = document.getElementById('navp'), navn = document.getElementById('navn');
var NDAYS = track.children.length, vpos = NDAYS;
// 前後各複製一整組，捲進複製區後靜默歸位 → 循環沒有跳點
(function(){
  var real = Array.prototype.slice.call(track.children);
  for (var i = real.length - 1; i >= 0; i--) {
    var c = real[i].cloneNode(true);
    c.classList.add('clone');
    c.setAttribute('aria-hidden', 'true');
    track.insertBefore(c, track.firstChild);
  }
  real.forEach(function(el){
    var c = el.cloneNode(true);
    c.classList.add('clone');
    c.setAttribute('aria-hidden', 'true');
    track.appendChild(c);
  });
  markPast();
})();
function px(name, fb){
  var v = parseFloat(getComputedStyle(track).getPropertyValue(name));
  return isNaN(v) ? fb : v;
}
function panelStep(){
  var a = track.children[0], b = track.children[1];
  return b ? b.offsetLeft - a.offsetLeft : px('--dayw', 320) + px('--gap', 12);
}
function layout(){
  if (!document.documentElement.classList.contains('nv')) return;
  var nl = document.querySelector('.nlist'), car = document.querySelector('.ncar');
  var dayw = px('--dayw', 320), gap = px('--gap', 12);
  var W = track.clientWidth, step = dayw + gap, n = NDAYS;
  // 七天全部放得下 → 關閉輪播互動
  var full = (n * dayw + (n - 1) * gap) <= W;
  track.classList.toggle('full', full);
  nl.classList.toggle('full', full);
  navp.style.display = navn.style.display = full ? 'none' : '';
  if (full) {
    track.style.paddingLeft = track.style.paddingRight = '0px';
    track.scrollLeft = 0;
    car.style.setProperty('--fadeL', '0px');
    car.style.setProperty('--fadeR', '0px');
    return;
  }
  // 當天置中：左右各留 (可視寬 − 單日寬)/2，兩端的日子也能捲到正中
  var side = (W - dayw) / 2;
  track.style.paddingLeft = track.style.paddingRight = side + 'px';
  // 單側能完整顯示的鄰日數，以及最外側被切一半那天的可見寬度
  var m = Math.floor(side / step);
  var sliver = Math.max(0, side - m * step - gap);
  var f = sliver > 3 ? Math.min(Math.max(sliver, 18), 130) : 0;
  car.style.setProperty('--fadeL', f + 'px');
  car.style.setProperty('--fadeR', f + 'px');
  var r = car.getBoundingClientRect();
  navp.style.left = '23px';
  navn.style.left = (window.innerWidth - 23) + 'px';
}
window.addEventListener('resize', function(){ measureDock(); syncRows(); layout(); goDay(cur + NDAYS, false); updateDock(); });
// 各日的同一小時列取最大高度，讓七天橫向對齊；空班自然留白
var ndock = document.getElementById('ndock');
function measureDock(){
  var t = document.querySelector('.top');
  var h = Math.round(t.getBoundingClientRect().height);
  document.documentElement.style.setProperty('--dockH', h + 'px');
}
// 把 dock 的星期換成第 k 片面板（k 是軌道上的實際索引）
function setDockDay(k){
  var panel = track.children[k];
  if (!panel) return;
  var hd = panel.querySelector('.dhd');
  if (hd && ndock.dataset.k !== String(k)) {
    ndock.innerHTML = hd.innerHTML;
    ndock.dataset.k = String(k);
  }
  ndock.classList.toggle('istoday', panel.classList.contains('today'));
}
function updateDock(){
  if (!document.documentElement.classList.contains('nv')) return;
  setDockDay(vpos);
  var dockH = parseFloat(getComputedStyle(document.documentElement)
    .getPropertyValue('--dockH')) || 92;
  // 只有面板內的標頭「整個」捲進固定列底下之後才接手，否則會同時出現兩個星期
  var hd = (track.children[vpos] || {}).querySelector
    ? track.children[vpos].querySelector('.dhd') : null;
  var gone = hd ? hd.getBoundingClientRect().bottom <= dockH + 1
                : document.querySelector('.nlist').getBoundingClientRect().top < dockH;
  var show = gone && !track.classList.contains('full');
  ndock.classList.toggle('show', show);
  track.classList.toggle('pinned', show);
}
// 橫向捲動時即時跟隨（不等吸附結束），否則手機慣性滑動期間星期會停在舊的那天
var swipeRaf = 0;
track.addEventListener('scroll', function(){
  if (swipeRaf) return;
  swipeRaf = requestAnimationFrame(function(){
    swipeRaf = 0;
    if (track.classList.contains('full')) return;
    setDockDay(Math.round(track.scrollLeft / panelStep()));
  });
}, {passive: true});
var dockRaf = 0;
window.addEventListener('scroll', function(){
  if (dockRaf) return;
  dockRaf = requestAnimationFrame(function(){ dockRaf = 0; updateDock(); });
}, {passive: true});
function syncRows(){
  if (!document.documentElement.classList.contains('nv')) return;
  var gut = document.getElementById('ngut');
  var head = gut.querySelector('.ngc.head');
  var hs = [], hd = 0;
  var heads = track.querySelectorAll('.dgrp > .dhd');
  Array.prototype.forEach.call(heads, function(el){
    el.style.height = 'auto';
    hd = Math.max(hd, el.getBoundingClientRect().height);
  });
  Array.prototype.forEach.call(heads, function(el){ el.style.height = hd + 'px'; });
  Array.prototype.forEach.call(gut.querySelectorAll('.ngc[data-h]'), function(g){
    hs.push(g.dataset.h);
  });
  head.style.height = hd + 'px';
  hs.forEach(function(h){
    var rows = track.querySelectorAll('.hrow[data-h="' + h + '"]');
    var g = gut.querySelector('.ngc[data-h="' + h + '"]');
    var mx = 0;
    Array.prototype.forEach.call(rows, function(r){ r.style.height = 'auto'; });
    g.style.height = 'auto';
    Array.prototype.forEach.call(rows, function(r){
      mx = Math.max(mx, r.scrollHeight);
    });
    mx = Math.max(mx, g.scrollHeight);
    Array.prototype.forEach.call(rows, function(r){ r.style.height = mx + 'px'; });
    g.style.height = mx + 'px';
  });
}
function markCur(){
  Array.prototype.forEach.call(track.children, function(c, k){
    c.classList.toggle('cur', k === vpos);
  });
}
function goDay(v, smooth){
  if (track.classList.contains('full')) { vpos = NDAYS; cur = 0; return; }
  vpos = v;
  cur = ((v - NDAYS) % NDAYS + NDAYS) % NDAYS;
  markCur();
  updateDock();
  track.scrollTo({left: v * panelStep(), behavior: smooth ? 'smooth' : 'auto'});
}
// 停在複製區時，把捲動位置搬回中央那一組（畫面完全相同，看不出來）
function normalize(){
  if (vpos < NDAYS || vpos >= NDAYS * 2) {
    vpos = cur + NDAYS;
    track.scrollLeft = vpos * panelStep();
    markCur();
  }
}
navp.addEventListener('click', function(){ goDay(vpos - 1, true); });
navn.addEventListener('click', function(){ goDay(vpos + 1, true); });
var st;
track.addEventListener('scroll', function(){
  clearTimeout(st);
  st = setTimeout(function(){
    if (track.classList.contains('full')) return;
    vpos = Math.round(track.scrollLeft / panelStep());
    cur = ((vpos - NDAYS) % NDAYS + NDAYS) % NDAYS;
    markCur();
    normalize();
    updateDock();
  }, 110);
});
(function(){
  var down = false, x0 = 0, s0 = 0, moved = 0;
  track.addEventListener('pointerdown', function(e){
    if (e.pointerType === 'touch' || track.classList.contains('full')) return;
    down = true; moved = 0; x0 = e.clientX; s0 = track.scrollLeft;
    track.classList.add('drag');
  });
  track.addEventListener('pointermove', function(e){
    if (!down) return;
    var d = e.clientX - x0;
    if (Math.abs(d) > 3) moved = 1;
    track.scrollLeft = s0 - d;
  });
  function end(){
    if (!down) return;
    down = false; track.classList.remove('drag');
    goDay(Math.round(track.scrollLeft / panelStep()), true);
  }
  track.addEventListener('pointerup', end);
  track.addEventListener('pointercancel', end);
  track.addEventListener('pointerleave', end);
  track.addEventListener('click', function(e){ if (moved) e.preventDefault(); }, true);
})();
// 首次進入定位到今天（週一=0 … 週日=6）
(document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve())
  .then(function(){ measureDock(); syncRows(); layout(); goDay(cur + NDAYS, false); updateDock(); });
measureDock();
syncRows();
layout();
goDay(((new Date().getDay() + 6) % 7) + NDAYS, false);
updateDock();
