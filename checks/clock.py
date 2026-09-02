# 用固定時間跑檢查（驗證「今天」與「已開始」狀態）
FAKE_INIT = """(() => { const fixed = new Date('%s').getTime(); const OD = Date;
 function D(...a){ return a.length ? new OD(...a) : new OD(fixed); }
 D.now = () => fixed; D.parse = OD.parse; D.UTC = OD.UTC; D.prototype = OD.prototype;
 window.Date = D; })();"""
