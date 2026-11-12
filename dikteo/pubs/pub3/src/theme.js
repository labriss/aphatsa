// Couleurs de Diktéo (copie de src/lib/theme-colors.ts) et polices du design system.
import {loadFont as archivo} from '@remotion/google-fonts/Archivo';
import {loadFont as publicSans} from '@remotion/google-fonts/PublicSans';
import {loadFont as mono} from '@remotion/google-fonts/JetBrainsMono';

export const T = {
  fond: '#0E1412',
  fond2: '#151E1A',
  carte: 'rgba(231,237,234,0.06)',
  bord: 'rgba(231,237,234,0.12)',
  texte: '#E7EDEA',
  doux: '#9BA8A2',
  o1: '#E8650F',
  o2: '#C9480A',
  o3: '#A8350A',
  vert: '#2FBF71',
  rouge: '#E5484D',
  degrade: 'linear-gradient(135deg, #E8650F 0%, #C9480A 55%, #A8350A 100%)',
  // Personnage
  peau: '#C98E68',
  peauOmbre: '#B07854',
  cheveux: '#2B211C',
  veste: '#24493B',
  vesteOmbre: '#1B382D',
  tshirt: '#D9DED9',
};

export const F = {
  titre: archivo('normal', {weights: ['800', '900']}).fontFamily,
  texte: publicSans('normal', {weights: ['400', '600', '700']}).fontFamily,
  mono: mono('normal', {weights: ['500', '700']}).fontFamily,
};

export const BRAND_MARK_PATH =
  'M6.5 2.5H12a9 9 0 0 1 0 18H9.2L4.5 23V4.5a2 2 0 0 1 2-2ZM9.2 9.5a1 1 0 0 0-1 1v2a1 1 0 0 0 2 0v-2a1 1 0 0 0-1-1Zm3.1-2.5a1 1 0 0 0-1 1v7a1 1 0 0 0 2 0V8a1 1 0 0 0-1-1Zm3.1 2a1 1 0 0 0-1 1v3a1 1 0 0 0 2 0v-3a1 1 0 0 0-1-1Z';
