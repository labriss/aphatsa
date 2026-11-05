// Cartes d'interface « premium » (inspiration 21st.dev) : verre dépoli, liseré, halo, typographie nette.
import React from 'react';
import {T, F, BRAND_MARK_PATH} from './theme';

export const Carte = ({children, style, halo}) => (
  <div style={{
    background: 'linear-gradient(180deg, rgba(231,237,234,0.10), rgba(231,237,234,0.04))',
    border: `1.5px solid ${T.bord}`, borderRadius: 28, padding: '22px 26px',
    backdropFilter: 'blur(18px)', boxShadow: `0 20px 60px rgba(0,0,0,0.45)${halo ? `, 0 0 80px ${halo}` : ''}`,
    color: T.texte, fontFamily: F.texte, ...style,
  }}>{children}</div>
);

export const Horloge = ({heure, style}) => (
  <Carte style={{display: 'flex', alignItems: 'center', gap: 16, ...style}}>
    <svg width={44} height={44} viewBox="0 0 44 44"><circle cx={22} cy={22} r={19} fill="none" stroke={T.doux} strokeWidth={3} />
      <path d="M22 10 V22 L30 27" stroke={T.texte} strokeWidth={3.5} strokeLinecap="round" fill="none" /></svg>
    <span style={{fontFamily: F.mono, fontWeight: 700, fontSize: 52, letterSpacing: -1}}>{heure}</span>
  </Carte>
);

export const Notif = ({titre, texte, icone = '!', couleur = T.rouge, style}) => (
  <Carte style={{display: 'flex', gap: 18, alignItems: 'center', ...style}}>
    <div style={{width: 64, height: 64, borderRadius: 18, background: couleur, display: 'grid', placeItems: 'center',
      fontFamily: F.titre, fontWeight: 900, fontSize: 36, color: '#fff', flexShrink: 0}}>{icone}</div>
    <div>
      <div style={{fontWeight: 700, fontSize: 26, color: T.doux}}>{titre}</div>
      <div style={{fontWeight: 600, fontSize: 32, lineHeight: 1.2}}>{texte}</div>
    </div>
  </Carte>
);

export const Jauge = ({valeur, style}) => {
  const c = valeur > 0.75 ? T.rouge : T.o1;
  return (
    <Carte style={{...style}} halo={valeur > 0.75 ? 'rgba(229,72,77,0.35)' : undefined}>
      <div style={{display: 'flex', justifyContent: 'space-between', fontWeight: 700, fontSize: 26, color: T.doux, marginBottom: 14}}>
        <span>Niveau d'agacement</span><span style={{fontFamily: F.mono, color: c}}>{Math.round(valeur * 100)} %</span>
      </div>
      <div style={{height: 22, borderRadius: 11, background: 'rgba(231,237,234,0.10)', overflow: 'hidden'}}>
        <div style={{width: `${valeur * 100}%`, height: '100%', borderRadius: 11,
          background: valeur > 0.75 ? `linear-gradient(90deg, ${T.o1}, ${T.rouge})` : T.degrade, boxShadow: `0 0 24px ${c}`}} />
      </div>
    </Carte>
  );
};

export const Logo = ({taille = 120, style, encre}) => (
  <div style={{display: 'flex', alignItems: 'center', gap: taille * 0.22, ...style}}>
    <div style={{width: taille, height: taille, borderRadius: taille * 0.28, background: T.degrade, display: 'grid', placeItems: 'center',
      boxShadow: '0 0 60px rgba(232,101,15,0.45)'}}>
      <svg width={taille * 0.62} height={taille * 0.62} viewBox="0 0 24 24"><path d={BRAND_MARK_PATH} fill="#fff" fillRule="evenodd" /></svg>
    </div>
    <span style={{fontFamily: F.titre, fontWeight: 900, fontSize: taille * 0.72, color: encre ? '#14100E' : T.texte, letterSpacing: -2}}>Diktéo</span>
  </div>
);

// Le téléphone avec le vrai écran de devis (données de l'exemple plombier du site).
export const Telephone = ({lignes = 4, onde = 0, accepte = false, style}) => {
  const L = [
    ['Chauffe-eau électrique 200 L', '520,00 €'],
    ['Groupe de sécurité et raccords', '48,00 €'],
    ["Dépose de l'ancien ballon", '60,00 €'],
    ["Main-d'œuvre · 3 h", '165,00 €'],
  ];
  return (
    <div style={{width: 430, height: 880, borderRadius: 64, background: '#05080A', padding: 14,
      boxShadow: '0 40px 120px rgba(0,0,0,0.6), 0 0 0 2px #2A3330', ...style}}>
      <div style={{width: '100%', height: '100%', borderRadius: 52, background: T.fond, overflow: 'hidden', position: 'relative',
        fontFamily: F.texte, color: T.texte, padding: '70px 26px 0'}}>
        <div style={{position: 'absolute', top: 18, left: '50%', transform: 'translateX(-50%)', width: 120, height: 34, borderRadius: 17, background: '#000'}} />
        <div style={{fontFamily: F.titre, fontWeight: 800, fontSize: 38}}>Nouveau devis</div>
        <div style={{fontSize: 20, color: T.doux, marginBottom: 18}}>Mme Fontaine · Villeurbanne</div>
        {L.slice(0, lignes).map(([d, p], i) => (
          <div key={i} style={{background: T.fond2, border: `1px solid ${T.bord}`, borderRadius: 18, padding: '14px 16px', marginBottom: 10,
            display: 'flex', justifyContent: 'space-between', fontSize: 19, fontWeight: 600}}>
            <span>{d}</span><span style={{fontFamily: F.mono, whiteSpace: 'nowrap', marginLeft: 12}}>{p}</span>
          </div>
        ))}
        {lignes >= 4 && (
          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', margin: '18px 4px'}}>
            <span style={{color: T.doux, fontSize: 20}}>Total TTC</span>
            <span style={{fontFamily: F.mono, fontWeight: 700, fontSize: 40}}>872,30 €</span>
          </div>
        )}
        <div style={{position: 'absolute', left: 26, right: 26, bottom: 30}}>
          {accepte ? (
            <div style={{height: 72, borderRadius: 20, background: T.vert, display: 'grid', placeItems: 'center', fontWeight: 700, fontSize: 24}}>✓ Accepté par Mme Fontaine</div>
          ) : (
            <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16}}>
              <div style={{display: 'flex', gap: 5, alignItems: 'center', height: 60}}>
                {Array.from({length: 22}, (_, i) => (
                  <div key={i} style={{width: 6, borderRadius: 3, background: T.o1, height: 8 + onde * 50 * Math.abs(Math.sin(i * 1.7 + onde * 9))}} />
                ))}
              </div>
              <div style={{width: 92, height: 92, borderRadius: 46, background: T.degrade, display: 'grid', placeItems: 'center',
                boxShadow: '0 0 50px rgba(232,101,15,0.55)'}}>
                <svg width={40} height={40} viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth={2.2} strokeLinecap="round">
                  <rect x={9} y={3} width={6} height={11} rx={3} /><path d="M5 11a7 7 0 0 0 14 0M12 18v3" /></svg>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
