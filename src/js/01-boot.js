// 01-boot.js — 在畫面繪製前決定版型，避免閃動；必須最先執行
(function(){var v;try{v=localStorage.getItem('yoga-view')}catch(e){}
if(v!=='n'&&v!=='w')v=(window.innerWidth||1200)<900?'n':'w';
document.documentElement.className=(v==='n'?'nv':'wv')})();
