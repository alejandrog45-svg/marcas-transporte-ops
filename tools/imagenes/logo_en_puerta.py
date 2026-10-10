# Genera las fotos de Aereostar con su logo integrado en la puerta del furgón (quita el logo de UberTransfer y el escudo de la camisa).
# Las fotos originales las envió el dueño y NO están en el repositorio: pasar su carpeta en U. Requiere numpy y Pillow (el CI no los usa).
import numpy as np
from PIL import Image, ImageFilter
U='/root/.claude/uploads/519e28ed-3947-5727-ad5c-7a01c30772cc/'
S='/tmp/claude-0/-home-user/519e28ed-3947-5727-ad5c-7a01c30772cc/scratchpad/'
R='/home/user/marcas-transporte-ops/'
rng=np.random.default_rng(7)
logo=Image.open(R+'docs/archivo/logo/logoaereostar.png').convert('RGB')
L=np.asarray(logo).astype(float); mx=L.max(-1); alpha=np.clip((mx-40)/110,0,1)
H,W=alpha.shape; yy,xx=np.mgrid[:H,:W]; alpha[np.hypot(xx-W/2,yy-H/2)>W*0.43]=0
ys,xs=np.where(alpha>0.3); bx=(xs.min(),ys.min(),xs.max()+1,ys.max()+1)
rgb=np.clip(L/np.maximum(alpha[...,None],0.05),0,255)
def wordmark(dark):
    c=rgb.copy()
    if dark:
        sat=c.max(-1)-c.min(-1); c[(sat<60)&(c.mean(-1)>150)]=[30,33,42]
    return Image.fromarray(np.dstack([c,alpha*255]).astype('uint8'),'RGBA').crop(bx)
def inpaint(a,hull,thr,dil=5,iters=1500,grain=3.0):
    x0,y0,x1,y1=hull; reg=a[y0:y1,x0:x1].copy(); med=np.median(reg.reshape(-1,3),axis=0)
    m=(np.abs(reg-med).sum(-1)>thr)
    m=np.asarray(Image.fromarray((m*255).astype('uint8')).filter(ImageFilter.MaxFilter(dil)))>0
    pad=10; X0,Y0,X1,Y1=x0-pad,y0-pad,x1+pad,y1+pad
    Rr=a[Y0:Y1,X0:X1].copy(); M=np.zeros(Rr.shape[:2],bool); M[pad:pad+m.shape[0],pad:pad+m.shape[1]]=m
    f=Rr.copy(); f[M]=Rr[~M].mean(0)
    for _ in range(iters):
        p=np.pad(f,((1,1),(1,1),(0,0)),mode='edge'); avg=(p[:-2,1:-1]+p[2:,1:-1]+p[1:-1,:-2]+p[1:-1,2:])/4; f[M]=avg[M]
    f=f+rng.normal(0,grain,f.shape[:2])[...,None]*M[...,None]   # grano para que no quede plástico
    w=(np.asarray(Image.fromarray((M*255).astype('uint8')).filter(ImageFilter.GaussianBlur(1.5)))/255.)[...,None]
    a[Y0:Y1,X0:X1]=Rr*(1-w)+f*w; return a
def decal(base,wm,cx,cy,w,rot=0,gain=(0.55,0.95),am=.92,blur=.8,spec=0.18):
    """Pega el logo como vinilo: perspectiva, luz de la puerta, brillo y grano."""
    h=round(wm.height*w/wm.width); d=wm.resize((w,h),Image.LANCZOS)
    pw,ph=w+20,h+20; canvas=Image.new('RGBA',(pw,ph),(0,0,0,0)); canvas.paste(d,(10,10))
    canvas=canvas.rotate(rot,resample=Image.BICUBIC,expand=True)
    arr=np.asarray(canvas).astype(float); al=arr[...,3]/255.
    x0=int(cx-canvas.width/2); y0=int(cy-canvas.height/2)
    bgreg=np.asarray(base.crop((x0,y0,x0+canvas.width,y0+canvas.height)).convert('RGB')).astype(float)
    lum=bgreg.mean(-1); ln=(lum-lum.mean())/(lum.std()+1e-6)
    light=np.clip(gain[0]+gain[1]*(lum/ max(lum.max(),1))*1.0,0.45,1.15)         # el vinilo recibe la luz del fondo
    col=arr[...,:3]*light[...,None]
    hi=np.clip(ln,0,None)[...,None]*spec*255*(al[...,None]>0.2)                   # brillo especular donde la puerta refleja
    col=np.clip(col+hi,0,255)
    col+=rng.normal(0,1.3,col.shape[:2])[...,None]                              # mismo grano que la foto
    a2=al*am
    out=bgreg*(1-a2[...,None])+col*a2[...,None]
    out=Image.fromarray(out.clip(0,255).astype('uint8'))
    res=base.convert('RGB').copy(); sm=out.filter(ImageFilter.GaussianBlur(blur))   # desenfoque suave del vinilo
    mask=Image.fromarray((np.clip(al*1.3,0,1)*255).astype('uint8')).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    res.paste(sm,(x0,y0),mask); return res
if __name__=='__main__':
    sat=lambda r:(r.max(-1)-r.min(-1))
    a=np.asarray(Image.open(U+'6ccf61f5-image.png').convert('RGB')).astype(float)
    a=inpaint(a,(655,886,775,1002),80,7,grain=1.3); a=inpaint(a,(936,802,970,834),60,5,grain=1.0)
    imgA=decal(Image.fromarray(a.clip(0,255).astype('uint8')),wordmark(False),716,944,104,rot=-2,gain=(0.66,0.62),spec=0.10,blur=.45)
    c=imgA.crop((560,560,1122,1010)); c.save(S+'ae6.png'); c.resize((900,round(c.height*900/c.width)),Image.LANCZOS).save(R+'site/bg/aereostar-sec-6.jpg',quality=62,optimize=True,progressive=True)
    imgA.crop((600,860,860,1040)).resize((780,540),Image.LANCZOS).save(S+'doorA.png')
    b=np.asarray(Image.open(U+'9fdeee7f-image.jpg').convert('RGB')).astype(float)
    b=inpaint(b,(580,826,698,932),50,9,grain=1.0); b=inpaint(b,(766,732,792,760),55,5,grain=1.0)
    imgB=decal(Image.fromarray(b.clip(0,255).astype('uint8')),wordmark(True),641,884,100,gain=(0.72,0.5),spec=0.08,blur=.45)
    d=imgB.crop((0,600,1024,940)); d.save(S+'ae4.png'); d.resize((1000,round(d.height*1000/d.width)),Image.LANCZOS).save(R+'site/bg/aereostar-banner-4.jpg',quality=62,optimize=True,progressive=True)
    imgB.crop((520,780,760,960)).resize((720,540),Image.LANCZOS).save(S+'doorB.png')
