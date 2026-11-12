// L'artisan en style BD / comics : contours d'encre épais, ombres en aplats (cel shading), expressions marquées.
// colere 0..1 · bouche : 'sourire' | 'grogne' | 'cri' | 'parle' · bras : 'bas' | 'poings' | 'ciel' | 'telephone'
import React from 'react';

const C = {
  encre: '#14100E',
  peau: '#E7A97F', peauO: '#C9845C',
  rouge: '#E2553F', rougeO: '#B83A28',
  chev: '#3B2A22', chevO: '#241811',
  veste: '#2E5A48', vesteO: '#1F4033',
  orange: '#F07A1E', orangeC: '#FFB067',
  tshirt: '#EFF1EC', tshirtO: '#C9CFC9',
  jean: '#2C3E4C', jeanO: '#1E2C37',
  blanc: '#FFFFFF',
};

const mix = (a, b, t) => {
  const p = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
  const [x, y] = [p(a), p(b)];
  return '#' + x.map((v, i) => Math.round(v + (y[i] - v) * t).toString(16).padStart(2, '0')).join('');
};

const S = {stroke: C.encre, strokeWidth: 7, strokeLinejoin: 'round', strokeLinecap: 'round'};

const Bras = ({pose, cote, peau, peauO}) => {
  // Épaule en (cote*118, 0) dans le repère du torse ; dessins en chemin pour garder un trait de BD.
  const s = cote;
  if (pose === 'ciel')
    return (
      <g>
        <path d={`M ${s * 95} 0 C ${s * 170} -40 ${s * 230} -150 ${s * 245} -270 L ${s * 195} -282 C ${s * 180} -175 ${s * 135} -95 ${s * 60} -25 Z`} fill={C.veste} {...S} />
        <path d={`M ${s * 236} -205 L ${s * 186} -215`} stroke={C.orange} strokeWidth={18} />
        <circle cx={s * 222} cy={-312} r={44} fill={peau} {...S} />
        <path d={`M ${s * 196} -330 q ${s * 26} -14 ${s * 52} 0 M ${s * 196} -310 q ${s * 26} -14 ${s * 52} 0`} stroke={peauO} strokeWidth={6} fill="none" />
      </g>
    );
  if (pose === 'poings')
    return (
      <g>
        <path d={`M ${s * 100} 10 C ${s * 160} 40 ${s * 175} 120 ${s * 120} 170 L ${s * 85} 140 C ${s * 120} 105 ${s * 110} 60 ${s * 70} 40 Z`} fill={C.veste} {...S} />
        <circle cx={s * 100} cy={168} r={40} fill={peau} {...S} />
      </g>
    );
  if (pose === 'telephone')
    return s < 0 ? (
      <g>
        <path d="M -100 10 C -175 40 -190 -60 -150 -120 L -110 -100 C -135 -60 -130 0 -70 30 Z" fill={C.veste} {...S} />
        <g transform="rotate(-14 -150 -170)">
          <rect x={-190} y={-250} width={84} height={150} rx={16} fill="#15201B" {...S} />
          <rect x={-180} y={-238} width={64} height={118} rx={8} fill="#0E1412" />
          <circle cx={-148} cy={-140} r={14} fill="#F07A1E" />
          {[0, 1, 2, 3, 4].map((i) => <rect key={i} x={-176 + i * 12} y={-200 - (i % 2) * 10} width={6} height={20 + (i % 2) * 20} rx={3} fill="#F07A1E" />)}
        </g>
        <circle cx={-142} cy={-112} r={38} fill={peau} {...S} />
      </g>
    ) : (
      <path d="M 100 10 C 140 60 140 170 120 250 L 85 245 C 95 170 90 80 70 40 Z" fill={C.veste} {...S} />
    );
  return <path d={`M ${s * 100} 10 C ${s * 140} 60 ${s * 140} 170 ${s * 120} 250 L ${s * 85} 245 C ${s * 95} 170 ${s * 90} 80 ${s * 70} 40 Z`} fill={C.veste} {...S} />;
};

export const ArtisanBD = ({colere = 0, bouche = 'grogne', brasG = 'bas', brasD = 'bas', vapeur = 0, sueur = 0, t = 0, regard = 0}) => {
  const k = Math.min(1, colere);
  const peau = mix(C.peau, C.rouge, k * 0.85);
  const peauO = mix(C.peauO, C.rougeO, k * 0.85);
  const fr = 8 + k * 26; // froncement des sourcils
  const tremble = k > 0.8 ? Math.sin(t * 3.1) * 5 : 0;
  return (
    <svg viewBox="-260 -420 520 900" width="100%" height="100%" style={{overflow: 'visible'}}>
      <g transform={`translate(${tremble} 0)`}>
        {/* Jambes */}
        <path d="M -95 250 L -105 455 L -20 455 L -10 270 Z" fill={C.jean} {...S} />
        <path d="M 95 250 L 105 455 L 20 455 L 10 270 Z" fill={C.jean} {...S} />
        <path d="M -60 270 L -70 450 L -20 450 L -12 280 Z" fill={C.jeanO} />
        <path d="M -125 440 Q -125 410 -60 412 L -10 420 L -10 470 L -125 470 Z" fill="#2B211C" {...S} />
        <path d="M 125 440 Q 125 410 60 412 L 10 420 L 10 470 L 125 470 Z" fill="#2B211C" {...S} />
        {/* Bras arrière */}
        <Bras pose={brasG} cote={-1} peau={peau} peauO={peauO} />
        <Bras pose={brasD} cote={1} peau={peau} peauO={peauO} />
        {/* Torse : veste de travail, bandes réfléchissantes */}
        <path d="M -110 20 Q -100 -15 -45 -22 L 45 -22 Q 100 -15 110 20 L 120 270 Q 0 290 -120 270 Z" fill={C.veste} {...S} />
        <path d="M 30 -10 Q 95 0 104 30 L 114 262 Q 70 272 40 274 Z" fill={C.vesteO} />
        <path d="M -40 -22 L 0 50 L 40 -22 Z" fill={C.tshirt} {...S} />
        <path d="M -118 150 L 118 150 L 119 180 L -119 180 Z" fill={C.orange} {...S} />
        <path d="M -116 156 L 116 156" stroke={C.orangeC} strokeWidth={5} />
        <path d="M 0 50 L 0 275" {...S} strokeWidth={5} />
        <rect x={-88} y={60} width={56} height={44} rx={8} fill={C.vesteO} {...S} strokeWidth={5} />
        {/* Cou */}
        <path d="M -38 -70 L -36 -18 L 36 -18 L 38 -70 Z" fill={peauO} {...S} />
        {/* Tête */}
        <ellipse cx={-118} cy={-170} rx={24} ry={34} fill={peau} {...S} />
        <ellipse cx={118} cy={-170} rx={24} ry={34} fill={peau} {...S} />
        <path d="M -110 -205 C -112 -300 -60 -330 0 -330 C 60 -330 112 -300 110 -205 L 104 -120 C 96 -70 50 -50 0 -50 C -50 -50 -96 -70 -104 -120 Z" fill={peau} {...S} />
        {/* Ombre du visage côté droit et barbe de trois jours */}
        <path d="M 60 -300 C 100 -280 112 -240 108 -200 L 102 -120 C 94 -80 64 -60 30 -54 C 70 -100 80 -200 60 -300 Z" fill={peauO} opacity={0.7} />
        <path d="M -98 -130 C -90 -70 -40 -56 0 -56 C 40 -56 90 -70 98 -130 C 70 -95 40 -88 0 -88 C -40 -88 -70 -95 -98 -130 Z" fill={C.chevO} opacity={0.22} />
        {/* Cheveux en mèches */}
        <path d="M -114 -200 C -130 -300 -60 -350 10 -345 C 80 -342 128 -300 112 -200 C 100 -250 70 -268 40 -262 C 20 -290 -20 -280 -30 -262 C -60 -275 -95 -255 -114 -200 Z" fill={C.chev} {...S} />
        <path d="M -60 -300 C -30 -320 20 -322 50 -305" stroke={C.chevO} strokeWidth={8} fill="none" strokeLinecap="round" />
        {/* Sourcils épais */}
        <path d="M -82 -222 L -22 -222 L -22 -204 L -82 -204 Z" fill={C.chev} {...S} strokeWidth={5} transform={`rotate(${fr} -22 -213)`} />
        <path d="M 82 -222 L 22 -222 L 22 -204 L 82 -204 Z" fill={C.chev} {...S} strokeWidth={5} transform={`rotate(${-fr} 22 -213)`} />
        {/* Yeux : blancs, pupilles, paupières lourdes quand il est énervé */}
        {[-1, 1].map((c) => (
          <g key={c}>
            <ellipse cx={c * 50} cy={-178} rx={24} ry={22 - k * 6} fill={C.blanc} {...S} strokeWidth={5} />
            <circle cx={c * 50 + regard * 6 - c * k * 3} cy={-176} r={9 - k * 2} fill={C.encre} />
            <circle cx={c * 50 + regard * 6 + 3} cy={-180} r={3} fill={C.blanc} />
            {k > 0.3 && <path d={`M ${c * 24} -196 L ${c * 76} ${-196 + c * 0}`} stroke={peauO} strokeWidth={9} strokeLinecap="round" />}
          </g>
        ))}
        {/* Nez */}
        <path d="M 4 -178 C -14 -150 -22 -128 -2 -122 C 12 -118 22 -126 20 -132" fill="none" {...S} strokeWidth={6} />
        {/* Bouche */}
        {bouche === 'sourire' && (
          <g>
            <path d="M -48 -100 Q 0 -50 48 -100 Q 0 -80 -48 -100 Z" fill="#7A2C1F" {...S} strokeWidth={6} />
            <path d="M -36 -96 Q 0 -86 36 -96 L 30 -88 Q 0 -80 -30 -88 Z" fill={C.blanc} />
          </g>
        )}
        {bouche === 'grogne' && (
          <g>
            <path d="M -46 -92 Q 0 -116 46 -92 L 40 -80 Q 0 -96 -40 -80 Z" fill="#5A2018" {...S} strokeWidth={6} />
            <path d="M -36 -90 L 36 -90" stroke={C.blanc} strokeWidth={8} />
          </g>
        )}
        {bouche === 'cri' && (
          <g>
            <path d="M -62 -120 Q 0 -140 62 -120 Q 66 -40 0 -32 Q -66 -40 -62 -120 Z" fill="#4A1610" {...S} />
            <path d="M -54 -120 Q 0 -134 54 -120 L 50 -104 Q 0 -114 -50 -104 Z" fill={C.blanc} />
            <path d="M -32 -48 Q 0 -70 32 -48 Q 0 -36 -32 -48 Z" fill="#D2564A" />
          </g>
        )}
        {bouche === 'parle' && <ellipse cx={0} cy={-96} rx={26} ry={10 + 8 * Math.abs(Math.sin(t * 0.9))} fill="#4A1610" {...S} strokeWidth={6} />}
        {/* Veine de colère */}
        {k > 0.5 && (
          <g transform="translate(64 -278)" opacity={Math.min(1, (k - 0.5) * 3)}>
            <path d="M -18 -8 Q -4 -2 -6 12 M 4 -18 Q 2 -4 16 -6 M 18 8 Q 4 4 6 -10 M -6 18 Q -2 4 -18 6" stroke="#C1121F" strokeWidth={8} fill="none" strokeLinecap="round" />
          </g>
        )}
        {/* Gouttes de sueur */}
        {sueur > 0 && <path d="M -128 -250 q -14 26 0 34 q 14 -8 0 -34 Z" fill="#9FD3F0" {...S} strokeWidth={5} opacity={sueur} />}
        {/* Vapeur */}
        {vapeur > 0 &&
          [-1, 1].map((c) =>
            [0, 1, 2].map((j) => {
              const u = (t / 14 + j / 3) % 1;
              return (
                <path key={`${c}${j}`} transform={`translate(${c * (150 + u * 70)} ${-180 - u * 120}) scale(${0.6 + u * 0.9})`}
                  d="M -30 0 C -40 -30 -10 -40 0 -28 C 10 -46 40 -36 32 -12 C 50 -8 46 20 26 22 C 20 38 -20 38 -24 22 C -46 22 -50 -2 -30 0 Z"
                  fill="#F4F4F4" {...S} strokeWidth={5} opacity={vapeur * (1 - u * 0.7)} />
              );
            }),
          )}
      </g>
    </svg>
  );
};
