// ——— les objets ———
const BLEU='#7fd0ff';
function flocon(x,y,r,col,lw=3){g.save();g.strokeStyle=col;g.lineWidth=lw;g.lineCap='round';g.translate(x,y);
  for(let i=0;i<3;i++){g.rotate(Math.PI/3);g.beginPath();g.moveTo(-r,0);g.lineTo(r,0);g.moveTo(r*.55,0);g.lineTo(r*.8,-r*.22);g.moveTo(r*.55,0);g.lineTo(r*.8,r*.22);g.moveTo(-r*.55,0);g.lineTo(-r*.8,-r*.22);g.moveTo(-r*.55,0);g.lineTo(-r*.8,r*.22);g.stroke();}g.restore();}
function climInt(k,on,t){if(k<=0)return;const {x,y,w,h}=CLIM;g.save();g.globalAlpha*=clamp(k*2);g.translate(0,(1-k)*-60);
  g.fillStyle='rgba(0,0,0,.35)';rr(x+10,y+16,w,h,30);g.fill();
  const gr=g.createLinearGradient(0,y,0,y+h);gr.addColorStop(0,'#f6f4f0');gr.addColorStop(.6,'#e4e1db');gr.addColorStop(1,'#c9c5bd');g.fillStyle=gr;rr(x,y,w,h,30);g.fill();
  g.fillStyle='rgba(0,0,0,.08)';g.fillRect(x+24,y+44,w-48,3);
  texte('INVERTER',x+40,y+82,18,'#9a958c',800,'Archivo','left');
  // l'afficheur : la consigne en bleu quand la clim tourne
  g.fillStyle='#1a1d20';rr(x+w-150,y+58,104,46,10);g.fill();
  if(on>0){g.save();lueur('rgba(127,208,255,.9)',14);texte(`${Math.round(lerp(35,24,on))}°`,x+w-98,y+82,30,BLEU,800,'JBMono');g.restore();}
  // le volet qui s'ouvre
  const a=.5*on;g.save();g.translate(x+30,y+h-18);g.rotate(a);g.fillStyle='#d4d0c8';rr(0,-8,w-60,16,8);g.fill();g.restore();
  g.fillStyle='rgba(0,0,0,.25)';g.fillRect(x+30,y+h-26,w-60,4);
  g.restore();}
// le souffle frais qui descend dans la pièce
function souffle(on,t){if(on<=0)return;const {x,y,w,h}=CLIM;g.save();g.globalCompositeOperation='lighter';g.lineCap='round';
  for(let i=0;i<7;i++){const bx=x+50+i*(w-100)/6;g.strokeStyle=`rgba(140,210,255,${.32*on})`;g.lineWidth=4;g.beginPath();
    for(let s=0;s<=24;s++){const L=s/24,yy=y+h+10+L*520*on,xx=bx+L*170+Math.sin(t*4-s*.45+i)*14*L;s?g.lineTo(xx,yy):g.moveTo(xx,yy);}g.stroke();}
  for(let i=0;i<14;i++){const ph=(t*.5+rnd(i*3.3))%1,px=x+60+rnd(i*1.7)*(w-120)+ph*190,py=y+h+20+ph*560*on;flocon(px,py,7+rnd(i)*5,`rgba(200,236,255,${.6*on*(1-ph)})`,2);}
  g.restore();}
function climExt(k,on,t){if(k<=0)return;const {x,y,w,h}=EXT;
  // le support mural : deux équerres sous l'unité
  g.save();g.globalAlpha*=clamp(k*2);g.strokeStyle='#3b3f44';g.lineWidth=10;g.lineCap='round';g.lineJoin='round';
  for(const ex of [x+40,x+w-40]){g.beginPath();g.moveTo(ex,y+h+4);g.lineTo(ex,y+h+46);g.moveTo(ex-30,y+h+4);g.lineTo(ex+30,y+h+4);g.moveTo(ex,y+h+40);g.lineTo(ex+26,y+h+6);g.stroke();}
  g.restore();
  g.save();g.globalAlpha*=clamp(k*2);const sy=.6+.4*clamp(k);g.translate(x+w/2,y+h);g.scale(1,sy);g.translate(-x-w/2,-y-h);
  g.fillStyle='rgba(0,0,0,.3)';rr(x+8,y+12,w,h,14);g.fill();
  const gr=g.createLinearGradient(x,0,x+w,0);gr.addColorStop(0,'#d9d6cf');gr.addColorStop(.5,'#f0ede7');gr.addColorStop(1,'#c3bfb7');g.fillStyle=gr;rr(x,y,w,h,14);g.fill();
  // la grille du ventilateur, qui tourne quand la clim démarre
  const cx=x+100,cy=y+h/2,r=62;g.fillStyle='#2a2d31';g.beginPath();g.arc(cx,cy,r,0,7);g.fill();
  g.save();g.translate(cx,cy);g.rotate(t*18*on);g.fillStyle='#5b6067';for(let i=0;i<3;i++){g.rotate(Math.PI*2/3);g.beginPath();g.ellipse(0,-28,14,28,.4,0,7);g.fill();}g.restore();
  g.strokeStyle='rgba(220,220,220,.5)';g.lineWidth=2;for(let rr2=18;rr2<r;rr2+=14){g.beginPath();g.arc(cx,cy,rr2,0,7);g.stroke();}
  g.fillStyle='rgba(0,0,0,.12)';for(let i=0;i<6;i++)g.fillRect(x+190,y+28+i*20,76,4);
  g.restore();}
function thermometre(temp,b){const {x,y,r}=THERMO;g.save();g.translate(x,y);
  g.fillStyle='rgba(0,0,0,.4)';g.beginPath();g.arc(6,10,r,0,7);g.fill();
  const gr=g.createRadialGradient(-20,-20,5,0,0,r);gr.addColorStop(0,'#f2efe9');gr.addColorStop(1,'#bdb8ae');g.fillStyle=gr;g.beginPath();g.arc(0,0,r,0,7);g.fill();
  g.fillStyle='#16191c';g.beginPath();g.arc(0,0,r*.74,0,7);g.fill();
  const u=clamp((temp-22)/13),chaud=u>.4;g.strokeStyle='rgba(255,255,255,.12)';g.lineWidth=7;g.beginPath();g.arc(0,0,r*.6,Math.PI*.75,Math.PI*2.25);g.stroke();
  g.strokeStyle=chaud?'#ff5a2a':BLEU;g.lineCap='round';g.beginPath();g.arc(0,0,r*.6,Math.PI*.75,Math.PI*(.75+1.5*u));g.stroke();
  lueur(chaud?'rgba(255,90,42,.8)':'rgba(127,208,255,.7)',12);texte(`${temp.toFixed(0)}°`,0,2,40,chaud?'#ffc2a8':'#d4efff',800,'JBMono');g.restore();}
function telecommande(k,on,b){if(k<=0)return;const {x,y}=TELE;g.save();g.translate(x,y);g.scale(clamp(k,0,1.1),clamp(k,0,1.1));
  g.fillStyle='rgba(0,0,0,.4)';rr(-50,-84,108,176,22);g.fill();g.fillStyle='#ece9e3';rr(-54,-90,108,176,22);g.fill();
  g.fillStyle='#1a1d20';rr(-38,-72,76,52,8);g.fill();
  const pret=b>=T_MO+.8;if(pret){lueur('rgba(127,208,255,.8)',10);flocon(-14,-46,11,BLEU,2.5);texte('OK',14,-45,18,BLEU,900,'Archivo');g.shadowBlur=0;}
  g.fillStyle=pret?O1:'#c9c5bd';g.beginPath();g.arc(0,16,16,0,7);g.fill();
  g.fillStyle='#c9c5bd';for(let i=0;i<2;i++)for(let j=0;j<2;j++){rr(-34+j*44,44+i*22,24,12,6);g.fill();}
  g.restore();}

function salon(b,t,h,kExt,on){
  // le mur : chaud orangé en pleine canicule, qui se rafraîchit en bleu-gris
  const gm=g.createLinearGradient(0,0,0,SOL);gm.addColorStop(0,mix([74,44,26],[30,40,52],h));gm.addColorStop(1,mix([92,56,32],[40,52,64],h));g.fillStyle=gm;g.fillRect(-400,-600,W+800,SOL+600);
  // la plinthe et le parquet
  const gs=g.createLinearGradient(0,SOL,0,H+400);gs.addColorStop(0,mix([110,70,40],[70,64,62],h));gs.addColorStop(1,mix([52,32,20],[26,26,30],h));g.fillStyle=gs;g.fillRect(-400,SOL,W+800,800);
  g.strokeStyle='rgba(0,0,0,.25)';g.lineWidth=3;for(let y=SOL+60;y<H+400;y+=70){g.beginPath();g.moveTo(-400,y);g.lineTo(W+400,y);g.stroke();}
  g.fillStyle=mix([140,100,70],[96,104,114],h);g.fillRect(-400,SOL-24,W+800,24);
  // la fenêtre : plein soleil d'été, les toits qui ondulent dans la chaleur
  const {x,y,w,h:fh}=FEN;const gc=g.createLinearGradient(0,y,0,y+fh);gc.addColorStop(0,'#ffcf7a');gc.addColorStop(.55,'#ffe6b0');gc.addColorStop(1,'#f3b36a');g.fillStyle=gc;g.fillRect(x,y,w,fh);
  g.save();g.beginPath();g.rect(x,y,w,fh);g.clip();
  const gsun=g.createRadialGradient(x+w*.72,y+110,10,x+w*.72,y+110,200);gsun.addColorStop(0,'rgba(255,255,240,1)');gsun.addColorStop(.25,'rgba(255,240,190,.9)');gsun.addColorStop(1,'rgba(255,200,120,0)');g.fillStyle=gsun;g.fillRect(x,y,w,fh);
  g.fillStyle='#fffdf2';g.beginPath();g.arc(x+w*.72,y+110,44,0,7);g.fill();
  g.fillStyle='#c98450';g.beginPath();g.moveTo(x,y+fh);for(let i=0;i<=12;i++){const xx=x+i*w/12,yy=y+fh-150-(i%3?30:70)+Math.sin(t*5+i)*2;g.lineTo(xx,yy);}g.lineTo(x+w,y+fh);g.fill();
  g.fillStyle='#a8683f';g.fillRect(x,y+fh-50,w,50);
  climExt(kExt,on,t);
  g.restore();
  // la vitre éblouie de soleil : l'éclat baisse quand la pièce se rafraîchit
  g.save();g.globalAlpha=.55*(1-h);g.drawImage(VITRE,x,y,w,fh);g.restore();
  g.strokeStyle=mix([214,196,170],[200,204,210],h);g.lineWidth=22;g.strokeRect(x,y,w,fh);g.lineWidth=12;g.beginPath();g.moveTo(x+w/2,y);g.lineTo(x+w/2,y+fh);g.stroke();
  // le rayon de soleil qui tape sur le parquet
  g.save();g.globalCompositeOperation='lighter';g.fillStyle=`rgba(255,190,110,${.13*(1-.7*h)})`;g.beginPath();g.moveTo(x,y);g.lineTo(x+w,y);g.lineTo(x+w-200,SOL+300);g.lineTo(x-420,SOL+300);g.closePath();g.fill();g.restore();
  // un fauteuil, pour lire le séjour
  g.fillStyle='rgba(0,0,0,.3)';rr(400,1290,170,180,24);g.fill();rr(390,1360,190,110,20);g.fill();
  // l'air brûlant qui ondule au-dessus du parquet
  if(h<.95){g.save();g.globalCompositeOperation='lighter';g.strokeStyle=`rgba(255,170,90,${.2*(1-h)})`;g.lineWidth=3;
    for(let i=0;i<8;i++){const bx=60+i*135;g.beginPath();for(let s=0;s<=22;s++){const yy=SOL-10-s*12,xx=bx+Math.sin(t*3+s*.5+i)*9;s?g.lineTo(xx,yy):g.moveTo(xx,yy);}g.stroke();}g.restore();}
}

function seek(T){
  const t=((T%DN)+DN)%DN,b=t/B;
  g.setTransform(1,0,0,1,0,0);g.globalAlpha=1;g.globalCompositeOperation='source-over';g.shadowBlur=0;g.setLineDash([]);g.filter='none';   // tout remettre à zéro à chaque image
  g.fillStyle='#050505';g.fillRect(0,0,W,H);
  const h=fraicheur(b),on=ease(seg(b,B_ON,B_ON+2));
  // la caméra : collée à la vitre brûlante, puis recul sur le séjour
  const kz=ease(seg(b,3.6,4.9));const cx=lerp(FEN.x+FEN.w/2,540,kz),cy=lerp(FEN.y+FEN.h/2,1000,kz),z=Math.exp(lerp(Math.log(2.9),Math.log(1),kz));
  g.save();g.translate(540,960);g.scale(z,z);g.translate(-cx,-cy);
  const kE=b>=T_TH?spring((b-T_TH)*B,12,.82):0;
  salon(b,t,h,kE,on);
  if(b>=T_TH){etincelles(EXT.x+EXT.w/2,EXT.y+EXT.h+20,31,(b-T_TH)*B/.6,.6,[150,215,255]);}
  // l'accroche : « CLIMATICIEN ? » balayé dans l'éblouissement de la vitre, l'air frais passe à travers
  if(b<5){const wipe=seg(b,.1,1.4);sg.setTransform(1,0,0,1,0,0);sg.clearRect(0,0,SCRATCH.width,SCRATCH.height);
    sg.globalCompositeOperation='source-over';sg.drawImage(VITRE,0,0);sg.globalCompositeOperation='destination-out';
    sg.font='900 92px Archivo';sg.textAlign='center';sg.textBaseline='middle';sg.lineJoin='round';sg.lineCap='round';sg.lineWidth=18;
    sg.save();sg.beginPath();sg.rect(0,0,SCRATCH.width*(.08+.9*wipe),SCRATCH.height);sg.clip();sg.strokeStyle='#000';sg.fillStyle='#000';sg.strokeText('CLIMATICIEN ?',SCRATCH.width/2,SCRATCH.height*.36);sg.fillText('CLIMATICIEN ?',SCRATCH.width/2,SCRATCH.height*.36);sg.restore();
    const {x,y,w,h:fh}=FEN;g.save();g.globalAlpha=1-seg(b,3.4,4.4);
    const gl=g.createRadialGradient(x+w/2,y+fh*.36,10,x+w/2,y+fh*.36,w*.6);gl.addColorStop(0,'rgba(60,150,230,.95)');gl.addColorStop(1,'rgba(20,70,140,.75)');g.fillStyle=gl;g.fillRect(x,y,w,fh);
    g.drawImage(SCRATCH,x,y,w,fh);
    // les lettres balayées restent nettes : l'air frais passe à travers
    g.save();g.beginPath();g.rect(x,y,w*(.08+.9*wipe),fh);g.clip();g.font='900 30.7px Archivo';g.textAlign='center';g.textBaseline='middle';lueur('rgba(90,180,255,.9)',6);g.fillStyle='#e4f4ff';g.fillText('CLIMATICIEN ?',x+w/2,y+fh*.36);g.restore();
    g.restore();}
  // 1 · le climatiseur se pose au mur
  const kc=b>=T_CH?spring((b-T_CH)*B,11,.82):0;climInt(kc,on,t);
  // 2 · la liaison frigorifique : le cuivre gainé court jusqu'à la fenêtre et descend vers l'unité extérieure
  if(b>=T_RAD){const u=ease(seg(b,T_RAD,T_RAD+1));g.save();g.lineCap='round';g.lineJoin='round';
    const pts=[[CLIM.x+CLIM.w-40,CLIM.y+CLIM.h],[CLIM.x+CLIM.w-40,790],[700,790],[700,EXT.y+10]];let L=0;const ls=[];for(let i=1;i<pts.length;i++){const l=Math.hypot(pts[i][0]-pts[i-1][0],pts[i][1]-pts[i-1][1]);ls.push(l);L+=l;}
    const trace=(col,lw)=>{let reste=L*u;g.strokeStyle=col;g.lineWidth=lw;g.beginPath();g.moveTo(...pts[0]);for(let i=1;i<pts.length&&reste>0;i++){const k=Math.min(1,reste/ls[i-1]);g.lineTo(lerp(pts[i-1][0],pts[i][0],k),lerp(pts[i-1][1],pts[i][1],k));reste-=ls[i-1];}g.stroke();};
    trace('#e9e6df',20);trace('#b5713f',7);
    // les deux colliers de fixation
    [[CLIM.x+CLIM.w-40,770],[600,790]].forEach(([px,py],i)=>{const b0=T_RAD+.3+i*.35;const k=b>=b0?spring((b-b0)*B,12,.82):0;if(k>0){g.save();g.translate(px,py);g.scale(k,k);g.fillStyle='#3b3f44';rr(-16,-16,32,32,8);g.fill();g.restore();}
      etincelles(px,py,i*17,(b-b0)*B/.6,.6,[150,215,255]);});
    g.restore();}
  // le souffle frais, quand la clim démarre
  souffle(on,t);
  // le thermomètre du séjour : 35° en pleine canicule, il redescend à 24°
  thermometre(lerp(35,24,h),b);
  // 4 · la mise en service : la télécommande
  telecommande(b>=T_MO?spring((b-T_MO)*B,12,.82):0,on,b);
  g.restore(); // fin de la caméra

  // la chaleur sur les bords de l'écran : elle tombe quand la clim démarre
  if(b>=3.6){g.save();g.globalAlpha=(1-h)*seg(b,3.6,4.8);g.drawImage(CHALEUR,0,0);g.restore();}
  // la lueur fraîche quand la clim tourne
  if(h>.4){g.save();g.globalCompositeOperation='lighter';const gl=g.createRadialGradient(330,900,100,330,900,1200);gl.addColorStop(0,`rgba(90,170,255,${.14*(h-.4)/.6})`);gl.addColorStop(1,'rgba(60,140,255,0)');g.fillStyle=gl;g.fillRect(0,0,W,H);g.restore();}

  // les étiquettes, une par ligne dictée
  FADE=1-seg(b,B_ON,B_ON+.5);
  etiquette('Clim réversible 3,5 kW','1 290 €',540,470,T_CH+.4,b);
  etiquette('Liaison 6 m','210 €',470,880,T_RAD+.5,b);
  etiquette('Support unité ext.','85 €',720,1100,T_TH+.4,b);
  etiquette('Mise en service','190 €',600,1230,T_MO+.4,b);
  // le contexte de l'accroche
  if(b>1.2&&b<4.6){const so=seg(b,3.9,4.4);g.save();g.globalAlpha=1-so;if(so>0)g.filter=`blur(${(so*8).toFixed(2)}px)`;lueur('rgba(0,0,0,.9)',24);
    motsFlous('Encore un devis à chiffrer',520,1480,44,'#f3e6d6',800,'Archivo','center',b,1.2);motsFlous('en pleine canicule ?',520,1544,44,'#ffb27a',800,'Archivo','center',b,2.2);g.restore();}
  // la phrase dite, en haut : une seule à la fois, avec le micro
  ITEMS.forEach((it,i)=>{const b1=i<ITEMS.length-1?ITEMS[i+1].b-.15:B_ON-.3;if(b<it.b-.05||b>b1+.2)return;
    const k=expoOut(seg(b,it.b-.05,it.b+.7)),a=k*(1-seg(b,b1,b1+.2));g.save();g.globalAlpha=a;g.translate(0,(1-k)*-18);
    g.fillStyle='rgba(10,8,6,.88)';rr(70,160,940,236,40);g.fill();
    const gm=g.createLinearGradient(110,223,190,303);gm.addColorStop(0,O1);gm.addColorStop(1,O3);g.fillStyle=gm;g.beginPath();g.arc(150,278,44,0,7);g.fill();
    g.fillStyle='#fff';rr(141,253,18,32,9);g.fill();g.strokeStyle='#fff';g.lineWidth=4;g.beginPath();g.arc(150,273,17,.15*Math.PI,.85*Math.PI);g.stroke();
    dictee(it,b,150,278,220,210,44);g.restore();});
  // la clim démarre : 24°, et le total
  if(b>=B_ON+.3&&b<B_ENV+.8){const kg=easeOut(seg(b,B_ON+.5,B_ON+2.3)),a=clamp((b-B_ON-.3)*3)*(1-seg(b,B_ENV+.2,B_ENV+.8)),val=TOTAL*kg;
    const txt=val.toLocaleString('fr-FR',{minimumFractionDigits:2,maximumFractionDigits:2}).replace(/ | /g,' ')+' €',fl=kg>=1?Math.exp(-(b-B_ON-2.3)*B*3):0;
    g.save();g.globalAlpha=a;g.fillStyle='rgba(12,10,8,.9)';rr(110,160,860,180,30);g.fill();g.strokeStyle='rgba(255,138,61,.35)';g.lineWidth=2;rr(110,160,860,180,30);g.stroke();
    texte('TOTAL TTC',150,250,30,'rgba(255,190,140,.8)',800,'Archivo','left');lueur(`rgba(255,138,61,${.6+.4*fl})`,18+40*fl);texte(txt,930,254,82,ORANGE,800,'JBMono','right');g.restore();}
  // l'envoi : le devis part par la fenêtre, une traînée fraîche dans le ciel brûlant
  if(b>=B_ENV&&b<B_FIN){const u=ease(seg(b,B_ENV,B_ENV+1.5));const P0=[540,1000],P1=[FEN.x+FEN.w/2,FEN.y+FEN.h/2],P2=[1200,-200];
    const at=v=>v<.5?[lerp(P0[0],P1[0],v*2),lerp(P0[1],P1[1],v*2)]:[lerp(P1[0],P2[0],v*2-1),lerp(P1[1],P2[1],v*2-1)];
    const [hx,hy]=at(u),fa=1-seg(b,B_ENV+1.3,B_ENV+1.6);g.save();g.globalAlpha=fa;g.globalCompositeOperation='lighter';
    g.beginPath();for(let i=0;i<=30;i++){const [px,py]=at(u*i/30);i?g.lineTo(px,py):g.moveTo(px,py);}g.strokeStyle='rgba(255,170,100,.5)';g.lineWidth=4;g.stroke();
    const gl=g.createRadialGradient(hx,hy,0,hx,hy,70);gl.addColorStop(0,'rgba(255,240,220,.95)');gl.addColorStop(.3,'rgba(255,160,80,.5)');gl.addColorStop(1,'rgba(255,120,40,0)');g.fillStyle=gl;g.beginPath();g.arc(hx,hy,70,0,7);g.fill();g.restore();}
  if(b>=B_TXT&&b<B_FIN+.2){const k=expoOut(seg(b,B_TXT,B_TXT+.8)),a=1-seg(b,B_FIN-.3,B_FIN+.1);g.save();g.globalAlpha=a;g.save();g.globalAlpha*=k;g.fillStyle='rgba(12,10,8,.86)';rr(130,1390,800,190,40);g.fill();g.restore();
    motsFlous('Envoyé à Mme Lefèvre.',530,1450,58,'#fff',800,'Archivo','center',b,B_TXT+.1);motsFlous('Avant la prochaine canicule.',530,1530,52,ORANGE,800,'Archivo','center',b,B_TXT+.75);g.restore();}
