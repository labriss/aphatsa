// Carton de fin « réaliste » de la pub 3 : après la bascule pixel → réalité.
import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {F, T} from './theme';
import {Logo} from './Ui';

export const Fin = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame: f, fps, config: {damping: 14, mass: 0.7}});
  const t2 = spring({frame: f - 8, fps, config: {damping: 18}});
  const t3 = spring({frame: f - 16, fps, config: {damping: 18}});
  return (
    <AbsoluteFill style={{background: `radial-gradient(70% 45% at 50% 42%, rgba(232,101,15,${0.28 * s}) 0%, #050607 70%)`}}>
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 70}}>
        <Logo taille={170} style={{transform: `scale(${0.7 + 0.3 * s})`, opacity: s}} />
        <div style={{fontFamily: F.titre, fontWeight: 900, fontSize: 84, lineHeight: 1.04, color: T.texte, textAlign: 'center', letterSpacing: -2,
          opacity: t2, transform: `translateY(${interpolate(t2, [0, 1], [40, 0])}px)`}}>
          Le devis du soir,<br /><span style={{color: T.o1}}>dicté en 30 s.</span>
        </div>
        <div style={{fontFamily: F.texte, fontWeight: 700, fontSize: 46, color: T.texte, padding: '22px 44px', borderRadius: 999,
          border: '2px solid rgba(231,237,234,0.25)', background: 'rgba(255,255,255,0.04)', opacity: t3,
          transform: `translateY(${interpolate(t3, [0, 1], [30, 0])}px)`}}>
          Gratuit · 3 devis par mois
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
