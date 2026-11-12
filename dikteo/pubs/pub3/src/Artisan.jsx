// L'artisan, dessiné en vectoriel : trait simple, aucun trait exagéré.
// colere : 0 (calme) → 1 (explose) : teint qui rougit, sourcils qui se froncent, veine, vapeur.
// bouche : 'neutre' | 'sourire' | 'grogne' | 'cri' | 'parle' ; ouverture : 0..1 (pour parler).
// brasG / brasD : angle des bras en degrés (0 = le long du corps, 90 = à l'horizontale, 160 = en l'air).
import React from 'react';
import {T} from './theme';

const mix = (a, b, t) => {
  const p = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
  const [x, y] = [p(a), p(b)];
  return '#' + x.map((v, i) => Math.round(v + (y[i] - v) * t).toString(16).padStart(2, '0')).join('');
};

const Bras = ({x, y, angle, cote, main}) => (
  <g transform={`translate(${x} ${y}) rotate(${cote * angle})`}>
    <path d={`M ${-24} 0 Q ${-30} 90 ${-20 * 1} 170 L ${22} 170 Q ${30} 90 ${24} 0 Z`} fill={T.veste} />
    <rect x={-22} y={120} width={44} height={14} rx={4} fill={T.o1} opacity={0.9} />
    <circle cx={0} cy={186} r={22} fill={main} />
  </g>
);

export const Artisan = ({colere = 0, bouche = 'neutre', ouverture = 0.5, brasG = 8, brasD = 8, regard = 0, vapeur = 0, tremble = 0, t = 0}) => {
  const peau = mix(T.peau, '#D8553F', Math.min(1, colere * 0.9));
  const ombre = mix(T.peauOmbre, '#B23A2A', Math.min(1, colere * 0.9));
  const dx = tremble ? Math.sin(t * 2.7) * 6 * tremble : 0;
  const froncement = colere * 22; // degrés
  const yeux = 1 - colere * 0.45;
  let mouth;
  if (bouche === 'sourire') mouth = <path d="M 168 268 Q 200 296 232 268" stroke="#5A2A1E" strokeWidth={7} fill="none" strokeLinecap="round" />;
  else if (bouche === 'grogne') mouth = <path d="M 172 280 Q 200 268 228 280" stroke="#5A2A1E" strokeWidth={7} fill="none" strokeLinecap="round" />;
  else if (bouche === 'cri')
    mouth = (
      <g>
        <ellipse cx={200} cy={282} rx={34} ry={26} fill="#4A1C14" />
        <rect x={176} y={260} width={48} height={10} rx={3} fill="#F4F1EC" />
        <ellipse cx={200} cy={296} rx={18} ry={7} fill="#C2564A" />
      </g>
    );
  else if (bouche === 'parle') mouth = <ellipse cx={200} cy={278} rx={20} ry={4 + 14 * ouverture} fill="#4A1C14" />;
  else mouth = <path d="M 180 276 L 220 276" stroke="#5A2A1E" strokeWidth={7} strokeLinecap="round" />;

  return (
    <svg viewBox="0 0 400 760" width="100%" height="100%" style={{overflow: 'visible'}}>
      <g transform={`translate(${dx} 0)`}>
        {/* Jambes */}
        <rect x={140} y={560} width={52} height={190} rx={18} fill="#1D2B33" />
        <rect x={208} y={560} width={52} height={190} rx={18} fill="#1D2B33" />
        <rect x={130} y={728} width={72} height={30} rx={12} fill="#2B211C" />
        <rect x={198} y={728} width={72} height={30} rx={12} fill="#2B211C" />
        {/* Bras derrière le corps */}
        <Bras x={112} y={392} angle={brasG} cote={1} main={peau} />
        <Bras x={288} y={392} angle={brasD} cote={-1} main={peau} />
        {/* Corps : veste de travail, bandes orange */}
        <path d="M 110 400 Q 120 368 160 360 L 240 360 Q 280 368 290 400 L 300 590 Q 200 610 100 590 Z" fill={T.veste} />
        <path d="M 170 360 L 200 420 L 230 360 Z" fill={T.tshirt} />
        <rect x={104} y={500} width={192} height={18} fill={T.o1} />
        <rect x={104} y={500} width={192} height={6} fill="#FFB37A" opacity={0.6} />
        <path d="M 200 420 L 200 590" stroke={T.vesteOmbre} strokeWidth={5} />
        <rect x={130} y={430} width={44} height={36} rx={6} fill={T.vesteOmbre} />
        {/* Cou */}
        <rect x={176} y={318} width={48} height={50} rx={14} fill={ombre} />
        {/* Tête */}
        <ellipse cx={128} cy={232} rx={18} ry={26} fill={ombre} />
        <ellipse cx={272} cy={232} rx={18} ry={26} fill={ombre} />
        <rect x={128} y={120} width={144} height={210} rx={70} fill={peau} />
        {/* Barbe de trois jours */}
        <path d="M 134 250 Q 140 330 200 334 Q 260 330 266 250 Q 240 300 200 300 Q 160 300 134 250 Z" fill={ombre} opacity={0.45} />
        {/* Cheveux */}
        <path d="M 126 196 Q 120 110 200 104 Q 282 108 276 196 Q 262 150 226 146 Q 196 160 150 150 Q 132 166 126 196 Z" fill={T.cheveux} />
        {/* Sourcils */}
        <rect x={148} y={182} width={42} height={11} rx={5} fill={T.cheveux} transform={`rotate(${froncement} 190 188)`} />
        <rect x={210} y={182} width={42} height={11} rx={5} fill={T.cheveux} transform={`rotate(${-froncement} 210 188)`} />
        {/* Yeux */}
        <ellipse cx={170} cy={216} rx={12} ry={14 * yeux} fill="#F4F1EC" />
        <ellipse cx={230} cy={216} rx={12} ry={14 * yeux} fill="#F4F1EC" />
        <circle cx={172 + regard * 4} cy={218} r={6.5} fill="#2A1E18" />
        <circle cx={232 + regard * 4} cy={218} r={6.5} fill="#2A1E18" />
        {/* Nez */}
        <path d="M 200 222 Q 188 248 202 252" stroke={ombre} strokeWidth={6} fill="none" strokeLinecap="round" />
        {mouth}
        {/* Veine de colère (style manga) */}
        {colere > 0.55 && (
          <g transform="translate(246 150)" opacity={Math.min(1, (colere - 0.55) * 3)}>
            <path d="M 0 0 l 10 10 m 4 -14 l -4 8 m 8 6 l -10 -2 m -6 8 l 4 -10" stroke="#B3261E" strokeWidth={5} strokeLinecap="round" />
          </g>
        )}
        {/* Vapeur qui sort des oreilles */}
        {vapeur > 0 &&
          [0, 1].map((i) =>
            [0, 1, 2].map((k) => {
              const u = ((t / 12 + k / 3) % 1);
              const sx = i ? 296 : 104;
              return (
                <circle key={`${i}${k}`} cx={sx + (i ? 1 : -1) * (14 + u * 50)} cy={226 - u * 90} r={12 + u * 22}
                  fill="#EDEDED" opacity={vapeur * (1 - u) * 0.85} />
              );
            }),
          )}
      </g>
    </svg>
  );
};
