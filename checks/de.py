import colorsys, math
def hls2hex(h,l,s):
    r,g,b=colorsys.hls_to_rgb(h,l,s); return "#%02X%02X%02X"%(round(r*255),round(g*255),round(b*255))
def hx(c):
    c=c.lstrip('#'); return tuple(int(c[i:i+2],16) for i in (0,2,4))
def lab(c):
    r,g,b=[v/255 for v in hx(c)]
    f=lambda v: v/12.92 if v<=0.04045 else ((v+0.055)/1.055)**2.4
    r,g,b=f(r),f(g),f(b)
    X=(0.4124*r+0.3576*g+0.1805*b)/0.95047; Y=(0.2126*r+0.7152*g+0.0722*b); Z=(0.0193*r+0.1192*g+0.9505*b)/1.08883
    g2=lambda t: t**(1/3) if t>0.008856 else 7.787*t+16/116
    fx,fy,fz=g2(X),g2(Y),g2(Z)
    return (116*fy-16, 500*(fx-fy), 200*(fy-fz))
def de00(c1,c2):
    L1,a1,b1=lab(c1); L2,a2,b2=lab(c2)
    C1=math.hypot(a1,b1); C2=math.hypot(a2,b2); Cb=(C1+C2)/2
    G=0.5*(1-math.sqrt(Cb**7/(Cb**7+25**7))) if Cb>0 else 0
    a1p,a2p=(1+G)*a1,(1+G)*a2
    C1p,C2p=math.hypot(a1p,b1),math.hypot(a2p,b2)
    h1=math.degrees(math.atan2(b1,a1p))%360; h2=math.degrees(math.atan2(b2,a2p))%360
    dL=L2-L1; dC=C2p-C1p; dh=h2-h1
    if C1p*C2p==0: dh=0
    elif dh>180: dh-=360
    elif dh<-180: dh+=360
    dH=2*math.sqrt(C1p*C2p)*math.sin(math.radians(dh)/2)
    Lb=(L1+L2)/2; Cbp=(C1p+C2p)/2
    if C1p*C2p==0: hbp=h1+h2
    else:
        s=h1+h2
        hbp=s/2 if abs(h1-h2)<=180 else ((s+360)/2 if s<360 else (s-360)/2)
    T=1-0.17*math.cos(math.radians(hbp-30))+0.24*math.cos(math.radians(2*hbp))+0.32*math.cos(math.radians(3*hbp+6))-0.20*math.cos(math.radians(4*hbp-63))
    dTh=30*math.exp(-((hbp-275)/25)**2)
    Rc=2*math.sqrt(Cbp**7/(Cbp**7+25**7))
    Sl=1+(0.015*(Lb-50)**2)/math.sqrt(20+(Lb-50)**2); Sc=1+0.045*Cbp; Sh=1+0.015*Cbp*T
    Rt=-Rc*math.sin(2*math.radians(dTh))
    return math.sqrt((dL/Sl)**2+(dC/Sc)**2+(dH/Sh)**2+Rt*(dC/Sc)*(dH/Sh))
def minde(cols):
    return min(de00(cols[i],cols[j]) for i in range(len(cols)) for j in range(i+1,len(cols)))
def worst(cols,names):
    p=[(de00(cols[i],cols[j]),names[i],names[j]) for i in range(len(cols)) for j in range(i+1,len(cols))]
    return sorted(p)[:5]
