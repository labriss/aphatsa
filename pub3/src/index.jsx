import React from 'react';
import {registerRoot, Still, AbsoluteFill, Composition} from 'remotion';
import {Fin} from './Fin';
import {T, F} from './theme';
import {Artisan} from './Artisan';
import {Horloge, Notif, Jauge, Logo, Telephone, Carte} from './Ui';
import {PlancheBD} from './PlancheBD';

const Fond = ({chaud = 0, children}) => (
  <AbsoluteFill style={{background: `radial-gradient(120% 80% at 50% 30%, ${chaud ? '#3A1A0E' : '#1A2621'} 0%, ${T.fond} 60%)`}}>
    <AbsoluteFill style={{backgroundImage: 'radial-gradient(rgba(231,237,234,0.07) 1.5px, transparent 1.5px)', backgroundSize: '36px 36px', opacity: 0.6}} />
    {children}
  </AbsoluteFill>
);

const Titre = ({children, haut = 150}) => (
  <div style={{position: 'absolute', top: haut, left: 70, right: 70, fontFamily: F.titre, fontWeight: 900, fontSize: 92, lineHeight: 1.02,
    color: T.texte, letterSpacing: -2}}>{children}</div>
);
const Em = ({children}) => <span style={{color: T.o1}}>{children}</span>;

const Camionnette = () => (
  <svg viewBox="0 0 700 360" width={760}>
    <rect x={20} y={60} width={470} height={230} rx={30} fill="#DCE2DE" />
    <path d="M 490 120 L 600 120 Q 640 124 660 190 L 670 290 L 490 290 Z" fill="#C9D0CB" />
    <path d="M 510 140 L 590 140 Q 615 146 628 200 L 510 200 Z" fill="#283A33" />
    <rect x={20} y={200} width={650} height={22} fill={T.o1} />
    <circle cx={150} cy={300} r={52} fill="#1A1F1D" /><circle cx={150} cy={300} r={22} fill="#7D8783" />
    <circle cx={560} cy={300} r={52} fill="#1A1F1D" /><circle cx={560} cy={300} r={22} fill="#7D8783" />
    {[0, 1, 2].map((k) => <circle key={k} cx={-10 - k * 40} cy={250 - k * 26} r={26 + k * 14} fill="#555" opacity={0.5 - k * 0.12} />)}
  </svg>
);

const Papier = ({x, y, r}) => (
  <div style={{position: 'absolute', left: x, top: y, width: 120, height: 156, background: '#F2EFE8', borderRadius: 6, transform: `rotate(${r}deg)`,
    boxShadow: '0 8px 20px rgba(0,0,0,0.35)', padding: 14}}>
    {[0, 1, 2, 3, 4].map((i) => <div key={i} style={{height: 7, background: '#C9C3B6', borderRadius: 4, marginBottom: 12, width: `${90 - i * 9}%`}} />)}
  </div>
);

// Planche 1 : la journée qui déborde
const Planche1 = () => (
  <Fond>
    <Titre>On a tous eu<br /><Em>cette journée.</Em></Titre>
    <div style={{position: 'absolute', left: -60, top: 1060}}><Camionnette /></div>
    <div style={{position: 'absolute', left: 520, top: 760, width: 460, height: 870}}><Artisan colere={0.62} bouche="grogne" brasG={30} brasD={110} /></div>
    <Horloge heure="17:42" style={{position: 'absolute', left: 70, top: 470}} />
    <Notif titre="Fournisseur" texte="Rupture de stock sur le chauffe-eau" style={{position: 'absolute', left: 70, right: 70, top: 600}} />
    <Jauge valeur={0.68} style={{position: 'absolute', left: 70, right: 70, bottom: 110}} />
  </Fond>
);

// Planche 2 : 21 h, le devis de trop
const Planche2 = () => (
  <Fond chaud>
    <Titre>Et maintenant…<br /><Em>le devis.</Em></Titre>
    {[[60, 520, -24], [300, 470, 18], [690, 540, 34], [820, 900, -12], [40, 980, 40], [600, 380, -38], [880, 640, 8]].map(([x, y, r], i) => <Papier key={i} x={x} y={y} r={r} />)}
    <div style={{position: 'absolute', left: 250, top: 700, width: 580, height: 1100}}><Artisan colere={1} bouche="cri" brasG={150} brasD={150} vapeur={1} t={4} /></div>
    <Horloge heure="21:07" style={{position: 'absolute', right: 70, top: 410}} />
    <Jauge valeur={1} style={{position: 'absolute', left: 70, right: 70, bottom: 110}} />
  </Fond>
);

// Planche 3 : le lendemain, il dicte
const Planche3 = () => (
  <Fond>
    <Titre haut={130}>Tu le dis.<br /><Em>C'est fait.</Em></Titre>
    <div style={{position: 'absolute', left: -40, top: 820, width: 520, height: 990}}><Artisan colere={0} bouche="sourire" brasG={10} brasD={70} /></div>
    <Telephone lignes={4} onde={0.6} style={{position: 'absolute', right: 70, top: 470, transform: 'rotate(4deg)'}} />
    <Notif titre="Diktéo · maintenant" texte="Mme Fontaine a accepté le devis" icone="✓" couleur={T.vert}
      style={{position: 'absolute', left: 470, right: 50, top: 1420}} />
    <Logo taille={92} style={{position: 'absolute', left: 70, bottom: 110}} />
  </Fond>
);

const Racine = () => (
  <>
    <Composition id="Fin" component={Fin} width={1080} height={1920} fps={30} durationInFrames={54} />
      <Still id="Planche1" component={Planche1} width={1080} height={1920} />
    <Still id="Planche2" component={Planche2} width={1080} height={1920} />
    <Still id="PlancheBD" component={PlancheBD} width={1080} height={1920} />
    <Still id="Planche3" component={Planche3} width={1080} height={1920} />
  </>
);
registerRoot(Racine);
