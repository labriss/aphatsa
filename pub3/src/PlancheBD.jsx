// Planche de style BD : 3 cases (la journée qui énerve, l'explosion de 21 h, la solution).
import React from 'react';
import {AbsoluteFill} from 'remotion';
import {loadFont as bangers} from '@remotion/google-fonts/Bangers';
import {ArtisanBD} from './ArtisanBD';
import {F, T} from './theme';
import {Logo} from './Ui';

const BANG = bangers().fontFamily;
const ENCRE = '#14100E';
const PAPIER = '#F3EDE2';

const Trame = ({couleur, fond, taille = 18, opacite = 0.35}) => (
  <AbsoluteFill style={{background: fond}}>
    <AbsoluteFill style={{backgroundImage: `radial-gradient(${couleur} 32%, transparent 34%)`, backgroundSize: `${taille}px ${taille}px`, opacity: opacite}} />
  </AbsoluteFill>
);

const Rayons = ({couleur = '#fff', n = 28, opacite = 0.5}) => (
  <svg viewBox="-500 -500 1000 1000" style={{position: 'absolute', inset: 0, width: '100%', height: '100%'}} preserveAspectRatio="xMidYMid slice">
    {Array.from({length: n}, (_, i) => {
      const a = (i / n) * Math.PI * 2, b = a + Math.PI / n / 1.6;
      return <path key={i} d={`M 0 0 L ${Math.cos(a) * 900} ${Math.sin(a) * 900} L ${Math.cos(b) * 900} ${Math.sin(b) * 900} Z`} fill={couleur} opacity={opacite} />;
    })}
  </svg>
);

const Case = ({x, y, w, h, rot = 0, children}) => (
  <div style={{position: 'absolute', left: x, top: y, width: w, height: h, transform: `rotate(${rot}deg)`, border: `10px solid ${ENCRE}`,
    overflow: 'hidden', boxShadow: '10px 12px 0 rgba(20,16,14,0.9)', background: '#fff'}}>{children}</div>
);

const Recitatif = ({children, style}) => (
  <div style={{position: 'absolute', background: '#FFD84D', border: `6px solid ${ENCRE}`, padding: '8px 18px', fontFamily: F.titre, fontWeight: 900,
    fontSize: 40, color: ENCRE, textTransform: 'uppercase', letterSpacing: 1, ...style}}>{children}</div>
);

const Bulle = ({children, style, queue = 'bas-gauche', cri}) => (
  <div style={{position: 'absolute', ...style}}>
    <div style={{background: '#fff', border: `6px solid ${ENCRE}`, borderRadius: cri ? 12 : '50%', padding: cri ? '18px 26px' : '30px 40px',
      fontFamily: F.titre, fontWeight: 800, fontSize: 34, lineHeight: 1.1, color: ENCRE, textAlign: 'center', textTransform: 'uppercase',
      clipPath: cri ? 'polygon(0% 12%, 8% 0%, 20% 10%, 33% 0%, 46% 9%, 60% 0%, 72% 10%, 86% 0%, 100% 14%, 94% 30%, 100% 48%, 93% 64%, 100% 82%, 88% 100%, 72% 90%, 58% 100%, 44% 90%, 30% 100%, 16% 90%, 4% 100%, 6% 80%, 0% 64%, 6% 48%, 0% 30%)' : undefined}}>
      {children}
    </div>
    {!cri && (
      <svg width={70} height={60} style={{position: 'absolute', bottom: -48, [queue.includes('gauche') ? 'left' : 'right']: 60}}>
        <path d={queue.includes('gauche') ? 'M 6 0 L 60 0 L 10 54 Z' : 'M 64 0 L 10 0 L 60 54 Z'} fill="#fff" stroke={ENCRE} strokeWidth={6} strokeLinejoin="round" />
        <rect x={0} y={-6} width={70} height={8} fill="#fff" />
      </svg>
    )}
  </div>
);

const Onomatopee = ({children, style, couleur = '#FFD84D', taille = 120, rot = -8}) => (
  <div style={{position: 'absolute', fontFamily: BANG, fontSize: taille, color: couleur, transform: `rotate(${rot}deg)`, letterSpacing: 2,
    WebkitTextStroke: `8px ${ENCRE}`, paintOrder: 'stroke fill', textShadow: `8px 8px 0 ${ENCRE}`, ...style}}>{children}</div>
);

const Camionnette = () => (
  <svg viewBox="0 0 700 380" width="100%">
    {[0, 1, 2].map((k) => <path key={k} transform={`translate(${-20 - k * 46} ${230 - k * 40}) scale(${1 + k * 0.5})`}
      d="M -30 0 C -40 -30 -10 -40 0 -28 C 10 -46 40 -36 32 -12 C 50 -8 46 20 26 22 C 20 38 -20 38 -24 22 C -46 22 -50 -2 -30 0 Z" fill="#8A8F8C" stroke={ENCRE} strokeWidth={5} />)}
    <path d="M 20 70 Q 20 50 40 50 L 470 50 L 470 300 L 20 300 Z" fill="#EDEFEC" stroke={ENCRE} strokeWidth={8} strokeLinejoin="round" />
    <path d="M 470 110 L 600 110 Q 645 115 670 195 L 680 300 L 470 300 Z" fill="#DADDDA" stroke={ENCRE} strokeWidth={8} strokeLinejoin="round" />
    <path d="M 495 130 L 590 130 Q 618 138 632 200 L 495 200 Z" fill="#7FB3C9" stroke={ENCRE} strokeWidth={6} />
    <rect x={20} y={205} width={660} height={26} fill="#F07A1E" stroke={ENCRE} strokeWidth={6} />
    {[150, 565].map((cx) => <g key={cx}><circle cx={cx} cy={305} r={56} fill="#222" stroke={ENCRE} strokeWidth={8} /><circle cx={cx} cy={305} r={22} fill="#9AA" stroke={ENCRE} strokeWidth={5} /></g>)}
  </svg>
);

const Papier = ({x, y, r, s = 1}) => (
  <div style={{position: 'absolute', left: x, top: y, width: 110 * s, height: 140 * s, background: '#fff', border: `5px solid ${ENCRE}`, transform: `rotate(${r}deg)`, padding: 12}}>
    {[0, 1, 2, 3].map((i) => <div key={i} style={{height: 6, background: '#9A9389', marginBottom: 14, width: `${88 - i * 12}%`}} />)}
  </div>
);

export const PlancheBD = () => (
  <AbsoluteFill style={{background: PAPIER}}>
    {/* Case 1 : 7 h 02, la camionnette ne démarre pas */}
    <Case x={50} y={60} w={980} h={560} rot={-1.2}>
      <Trame fond="#BFE0EC" couleur="#6FA8BF" />
      <div style={{position: 'absolute', left: -30, top: 250, width: 640}}><Camionnette /></div>
      <div style={{position: 'absolute', left: 560, top: 70, width: 380, height: 660}}><ArtisanBD colere={0.45} bouche="grogne" brasG="poings" brasD="bas" sueur={1} /></div>
      <Recitatif style={{left: 24, top: 24}}>7 h 02</Recitatif>
      <Onomatopee style={{left: 40, top: 150}} taille={96} couleur="#F3EDE2">KRRR… KRRR…</Onomatopee>
      <Bulle style={{right: 300, top: 20, width: 330}} queue="bas-droite">Pas aujourd'hui…</Bulle>
    </Case>
    {/* Case 2 : 21 h 07, le devis de trop */}
    <Case x={40} y={660} w={1000} h={720} rot={1.4}>
      <Trame fond="#E8442E" couleur="#9E1F12" taille={22} opacite={0.45} />
      <Rayons couleur="#FFD84D" opacite={0.35} />
      {[[60, 120, -24], [800, 90, 22], [700, 420, -36], [90, 470, 30], [830, 300, 8], [240, 40, 14]].map(([x, y, r], i) => <Papier key={i} x={x} y={y} r={r} />)}
      <div style={{position: 'absolute', left: 250, top: 190, width: 500, height: 870}}><ArtisanBD colere={1} bouche="cri" brasG="ciel" brasD="ciel" vapeur={1} t={5} /></div>
      <Recitatif style={{left: 24, top: 24}}>21 h 07 · le devis</Recitatif>
      <Onomatopee style={{right: 30, top: 40}} taille={150} rot={10}>RAAAH !</Onomatopee>
    </Case>
    {/* Case 3 : le lendemain, il dicte */}
    <Case x={50} y={1420} w={980} h={450} rot={-0.8}>
      <Trame fond="#FFE7B8" couleur="#F0A84A" />
      <div style={{position: 'absolute', left: 60, top: 70, width: 330, height: 580}}><ArtisanBD colere={0} bouche="parle" brasG="telephone" brasD="bas" t={3} regard={-0.5} /></div>
      <Recitatif style={{left: 24, top: 24}}>Le lendemain</Recitatif>
      <Bulle style={{left: 360, top: 30, width: 340}}>Chauffe-eau 200 litres, 520 euros…</Bulle>
      <div style={{position: 'absolute', right: 26, top: 220, background: T.fond, border: `6px solid ${ENCRE}`, borderRadius: 22, padding: '16px 22px',
        fontFamily: F.texte, color: T.texte, width: 330}}>
        <div style={{fontSize: 22, color: T.doux, fontWeight: 600}}>Diktéo · maintenant</div>
        <div style={{fontSize: 28, fontWeight: 700}}>✓ Mme Fontaine a accepté le devis</div>
      </div>
      <Logo taille={56} encre style={{position: 'absolute', right: 30, bottom: 26}} />
    </Case>
  </AbsoluteFill>
);
