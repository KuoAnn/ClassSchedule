// 04-narrow.js — 窄版輪播：無限循環、當日置中、小時列對齊、釘住的整排星期
var track = document.getElementById('ntrack'), cur = 0;
var navp = document.getElementById('navp'), navn = document.getElementById('navn');
var NDAYS = track.children.length, vpos = NDAYS;
// dock 的參照要在複製面板之前就取得：下面那段 IIFE 會馬上 buildDock()
var ndock = document.getElementById('ndock'), ndockin = document.getElementById('ndockin');
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
  buildDock();
})();
function px(name, fb){
  var v = parseFloat(getComputedStyle(track).getPropertyValue(name));
  return isNaN(v) ? fb : v;
}
function panelStep(){
  var a = track.children[0], b = track.children[1];
  return b ? b.offsetLeft - a.offsetLeft : px('--dayw', 320) + px('--gap', 12);
}
function setFade(car, l, r){
  car.style.setProperty('--fadeL', l + 'px');
  car.style.setProperty('--fadeR', (r === undefined ? l : r) + 'px');
}
// 翻頁鈕靠 clientWidth 定位，不要用 innerWidth：innerWidth 含垂直捲軸的寬度，
// 桌機把窄版視窗縮小時鈕會被推到捲軸底下、右半邊看起來就是被切掉
function placeNav(){
  var W = document.documentElement.clientWidth || window.innerWidth;
  navp.style.left = '23px';
  navn.style.left = (W - 23) + 'px';
}
// 單日寬度是算出來的，不是寫死的 320px：手機夠寬就一次擺得下兩天以上，
// 不必一天一天滑。MINDAY 是「卡片還讀得下去」的下限（實測 150px：時段、老師、
// 暫停標籤都還放得進一行），MAXDAY 是原本的單日寬，不要因為螢幕大就把卡片拉更寬。
var MINDAY = 142, MAXDAY = 320;
function sizeDays(){
  // clientWidth 已經扣掉左側時間欄與 .sheet 的內距，也含 layout() 自己塞的置中 padding。
  // 再讓回一個 gap 的寬度，理由有兩個，缺一個就會看起來像卡片被切掉：
  //   1. 軌道是出血到螢幕邊的（.nlist 的 margin-right:-14px），不留白的話最後一欄
  //      的右框與圓角正好壓在邊界上；
  //   2. 讓回的剛好是一個 gap，下一欄的左緣就正好落在裁切邊上、露不出來 ——
  //      讓多一點會露出一條下一張卡的左側色條，讓少一點則是最後一欄貼死邊界。
  var gap = px('--gap', 12);
  var W = track.clientWidth - gap;
  if (W <= 0) return 1;
  var per = Math.max(1, Math.min(NDAYS, Math.floor((W + gap) / (MINDAY + gap))));
  var w = Math.min(MAXDAY, Math.floor((W - (per - 1) * gap) / per));
  document.documentElement.style.setProperty('--dayw', w + 'px');
  return per;
}
function layout(){
  if (!document.documentElement.classList.contains('nv')) return;
  var nl = document.querySelector('.nlist'), car = document.querySelector('.ncar');
  sizeDays();
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
    setFade(car, 0);
    return;
  }
  // 非 full 一律採「某一天置中」：進入窄版先以今天為定位、切換星期與拖拉放手都吸附到
  // 最近的置中定位點；其餘星期會由中間往兩側平均露出。
  var side = (W - dayw) / 2;
  track.style.paddingLeft = track.style.paddingRight = side + 'px';
  // 單側能完整顯示的鄰日數，以及最外側被切一半那天的可見寬度
  var m = Math.floor(side / step);
  var sliver = Math.max(0, side - m * step - gap);
  // 單日寬是整數，邊緣常會留下 1～2px 的半格殘影；只要有切到外側那天就開淡出，
  // 讓邊界看起來是柔化而不是卡片被切掉。
  var f = sliver > 0 ? Math.min(Math.max(sliver, 14), 130) : 0;
  setFade(car, f);
  placeNav();
}
// syncRows() 一定要排在 layout() 後面：layout() 會算出新的 --dayw，
// 卡片寬度變了換行就變了，先量高度等於拿舊寬度的結果去對齊
window.addEventListener('resize', function(){ measureDock(); layout(); syncRows(); goDay(cur + NDAYS, false); updateDock(); });
// 各日的同一小時列取最大高度，讓七天橫向對齊；空班自然留白
function measureDock(){
  var t = document.querySelector('.top');
  var h = Math.round(t.getBoundingClientRect().height);
  document.documentElement.style.setProperty('--dockH', h + 'px');
}
// dock 是輪播的鏡射：一格對一個面板（含前後兩組複製），順序與寬度都一樣，
// 這樣 translateX(-scrollLeft) 就能讓星期永遠停在自己那一欄的正上方。
// 一格對一個「真實日子」是不夠的 —— 慣性滑進複製區時 dock 會整排跑掉。
// 星期字樣直接抄面板標頭（中英雙語都在裡面，語言切換照舊靠 CSS）
function buildDock(){
  var f = document.createDocumentFragment();
  for (var i = 0; i < track.children.length; i++) {
    var panel = track.children[i];
    var dk = document.createElement('span');
    dk.className = 'dk' + (panel.classList.contains('today') ? ' today' : '');
    dk.innerHTML = panel.querySelector('.dday').innerHTML;
    var tdy = dk.querySelector('.tdy');
    if (tdy) tdy.remove();
    f.appendChild(dk);
  }
  ndockin.textContent = '';
  ndockin.appendChild(f);
}
// 跟著輪播位移（吃即時的 scrollLeft，慣性滑動途中也會跟著換），並打亮最左邊那天。
// 位移量就是 -scrollLeft：dock 的每一格與面板同寬同間距，又從時間欄右緣起算
function syncDock(){
  var k = track.classList.contains('full') ? cur
    : ((Math.round(track.scrollLeft / panelStep()) - NDAYS) % NDAYS + NDAYS) % NDAYS;
  ndockin.style.transform = 'translateX(' + (-track.scrollLeft) + 'px)';
  Array.prototype.forEach.call(ndockin.children, function(el, i){
    el.classList.toggle('on', i % NDAYS === k);
  });
}
function updateDock(){
  if (!document.documentElement.classList.contains('nv')) return;
  syncDock();
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
    syncDock();
  });
}, {passive: true});
var dockRaf = 0;
window.addEventListener('scroll', function(){
  if (dockRaf) return;
  dockRaf = requestAnimationFrame(function(){ dockRaf = 0; updateDock(); });
}, {passive: true});
// 窄版是全緊密排列，沒有跨日對齊可言，所以這裡只剩一件事：各日的標頭等高。
// 標頭是並排的，不齊的話每一欄的第一張卡會從不同高度開始。
// 名字留著不改：resize、切版型、切語言三處都在呼叫它。
function syncRows(){
  if (!document.documentElement.classList.contains('nv')) return;
  var hd = 0;
  var heads = track.querySelectorAll('.dgrp > .dhd');
  Array.prototype.forEach.call(heads, function(el){
    el.style.height = 'auto';
    hd = Math.max(hd, el.getBoundingClientRect().height);
  });
  Array.prototype.forEach.call(heads, function(el){ el.style.height = hd + 'px'; });
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
  .then(function(){ measureDock(); layout(); syncRows(); goDay(cur + NDAYS, false); updateDock(); });
measureDock();
layout();
syncRows();
goDay(((new Date().getDay() + 6) % 7) + NDAYS, false);
updateDock();
