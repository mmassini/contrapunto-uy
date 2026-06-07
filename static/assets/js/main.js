/* Contrapunto UY — Main JS */

// Color each bias-fill based on its width (position in gradient)
document.querySelectorAll('.bias-fill').forEach(el => {
  const pct = parseFloat(el.style.width) || 0;
  // Interpolate green→yellow→red
  let r, g, b;
  if (pct <= 50) {
    const t = pct / 50;
    r = Math.round(46 + t * (249 - 46));
    g = Math.round(125 - t * (125 - 168));
    b = Math.round(50 - t * (50 - 37));
  } else {
    const t = (pct - 50) / 50;
    r = Math.round(249 + t * (198 - 249));
    g = Math.round(168 - t * (168 - 40));
    b = Math.round(37 + t * (40 - 37));
  }
  el.style.background = `rgb(${r},${g},${b})`;
});
