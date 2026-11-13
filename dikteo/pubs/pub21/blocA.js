const ITEMS=[
  {b:5, dit:'« Clim réversible 3,5 kilowatts,', dit2:'1 290 euros. »'},
  {b:8, dit:'« Liaison frigo, six mètres,', dit2:'35 euros le mètre. »'},
  {b:11, dit:'« Support mural extérieur,', dit2:'85 euros. »'},
  {b:14,dit:'« Mise en service,', dit2:'190 euros. »'},
];
const T_CH=5.3, T_RAD=8.3, T_TH=11.3, T_MO=14.3, B_ON=16.6, B_ENV=20.4, B_TXT=21.2, B_FIN=24.4;
// 1 290 + 6 × 35 + 85 + 190 = 1 775 € HT ; TVA 10 % : 177,50 € ; TTC 1 952,50 €
const TOTAL=1952.5;
// la fraîcheur de la pièce, de 0 (canicule, 35°) à 1 (24°)
const fraicheur=b=>.1*ease(seg(b,T_CH+.5,T_CH+1.5))+.1*ease(seg(b,T_RAD+.4,T_RAD+1.6))+.1*ease(seg(b,T_TH+.4,T_TH+1.2))+.7*ease(seg(b,B_ON,B_ON+2.6));
// la pièce
const FEN={x:590,y:520,w:380,h:520};            // la fenêtre (dehors : le soleil qui tape)
const CLIM={x:100,y:590,w:420,h:150};           // le climatiseur mural (unité intérieure)
const EXT={x:640,y:830,w:290,h:160};            // l'unité extérieure, vue par la fenêtre, sur son support
const THERMO={x:200,y:1010,r:66};               // le thermomètre du séjour
const TELE={x:200,y:1250};                      // la télécommande au mur
const SOL=1480;

// la chaleur sur les bords de l'écran : un voile orange qui vibre, calculé une fois
const CHALEUR=(()=>{const c=document.createElement('canvas');c.width=W;c.height=H;const f=c.getContext('2d');
  const gr=f.createRadialGradient(W/2,H/2,H*.28,W/2,H/2,H*.78);gr.addColorStop(0,'rgba(255,150,60,0)');gr.addColorStop(.6,'rgba(255,130,40,.14)');gr.addColorStop(1,'rgba(255,110,30,.42)');f.fillStyle=gr;f.fillRect(0,0,W,H);
  const gs=f.createRadialGradient(W*.9,0,0,W*.9,0,900);gs.addColorStop(0,'rgba(255,230,170,.35)');gs.addColorStop(1,'rgba(255,200,120,0)');f.fillStyle=gs;f.fillRect(0,0,W,H);
  return c;})();
// la vitre brûlée de soleil, pour l'accroche : un éblouissement blanc-orangé
const VITRE=(()=>{const c=document.createElement('canvas');c.width=FEN.w*3;c.height=FEN.h*3;const f=c.getContext('2d');
  const gr=f.createLinearGradient(0,0,c.width,c.height);gr.addColorStop(0,'rgba(255,236,190,.95)');gr.addColorStop(.5,'rgba(255,196,120,.92)');gr.addColorStop(1,'rgba(240,150,70,.9)');f.fillStyle=gr;f.fillRect(0,0,c.width,c.height);
  const gs=f.createRadialGradient(c.width*.8,c.height*.12,10,c.width*.8,c.height*.12,c.width*.7);gs.addColorStop(0,'rgba(255,255,240,.95)');gs.addColorStop(1,'rgba(255,220,160,0)');f.fillStyle=gs;f.fillRect(0,0,c.width,c.height);
  let s=5;const R=()=>(s=(s*16807)%2147483647)/2147483647;f.strokeStyle='rgba(255,255,235,.35)';f.lineCap='round';
  for(let i=0;i<26;i++){const x=R()*c.width*1.4-c.width*.2;f.lineWidth=6+R()*30;f.beginPath();f.moveTo(x,0);f.lineTo(x-c.height*.5,c.height);f.stroke();}
  return c;})();
const SCRATCH=document.createElement('canvas');SCRATCH.width=VITRE.width;SCRATCH.height=VITRE.height;const sg=SCRATCH.getContext('2d');

