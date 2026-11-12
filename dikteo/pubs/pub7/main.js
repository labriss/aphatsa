// Le Soir du plombier — entrée de la page : window.render(t) dessine l'image t.
const cv = document.getElementById('c'), g = cv.getContext('2d');
await Promise.all(['400 40px "Old Standard TT"', 'italic 400 40px "Old Standard TT"', '700 40px "Old Standard TT"', '900 40px "Playfair Display SC"', '700 40px "Playfair Display SC"'].map(f => document.fonts.load(f)));
const film = await import('./film.js');
window.EV = film.events();
window.DUR = film.DUR;
window.render = async t => { g.setTransform(1, 0, 0, 1, 0, 0); film.renderFilm(g, t); };
window.READY = true;
