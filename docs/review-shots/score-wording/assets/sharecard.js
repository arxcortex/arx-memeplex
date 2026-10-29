/* Arx Cortex share card: renders a 1080x1920 (9:16) PNG on a 2D canvas.
   window.ArxShareCard.single(data) / .compare(data) -> Promise<Blob>; .open(blob, filename) shows preview modal. */
(function () {
  const W = 1080, H = 1920, PAD = 84;
  // FOOTER ZONE: everything below SAFE belongs to the footer (rule at H-196, wordmark, URL). Content must end above it.
  const SAFE = H - 196 - 28; let low = 0; const mark = y => { low = Math.max(low, y); return y; };
  const C = { bg: '#0a0a0c', bg2: '#141217', ink: '#e8e2d4', dim: '#8a8478', faint: '#4a463e', amber: '#b87333', bright: '#e89968', rule: '#4a2810', blue: '#3d6f8a', blueL: '#6fa3c0' };
  const SERIF = "'Cormorant Garamond', Georgia, serif", MONO = "'JetBrains Mono', ui-monospace, monospace";
  const img = src => new Promise(r => { const i = new Image(); i.onload = () => r(i); i.onerror = () => r(null); i.src = src; });
  let assets;
  async function prep() {
    try { await Promise.all(['500 80px', '400 40px', 'italic 400 40px'].map(f => document.fonts.load(f + " 'Cormorant Garamond'")).concat(['400 24px', '500 24px'].map(f => document.fonts.load(f + " 'JetBrains Mono'")))); await document.fonts.ready; } catch (e) {}
    if (!assets) { const base = (window.ARX_BRAND_BASE || 'assets/brand/'); const [mark, sigil] = await Promise.all([img(base + 'wordmark-copper.png'), img(base + 'sigil-copper.png')]); assets = { mark, sigil }; }
  }
  const font = (x, f) => (x.font = f);
  function spaced(x, t, px, x0, y, align, maxW) { // letter-spaced mono caps, truncated to maxW (spacing included)
    const ls = x.letterSpacing !== undefined; if (ls) x.letterSpacing = px + 'px'; else t = t.split('').join(' ');
    if (maxW) t = trunc(x, t, maxW);
    x.textAlign = align || 'left'; x.fillText(t, x0, y); if (ls) x.letterSpacing = '0px';
  }
  // wrap into lines, at most maxLines; ellipsis on overflow; long single words are hard-broken
  function wrap(x, text, maxW, maxLines) {
    const words = String(text || '').split(/\s+/).filter(Boolean), lines = []; let cur = '';
    const push = w => { while (x.measureText(w).width > maxW) { let k = w.length; while (k > 1 && x.measureText(w.slice(0, k) + '-').width > maxW) k--; lines.push(w.slice(0, k) + '-'); w = w.slice(k); } return w; };
    for (let w of words) { const t = cur ? cur + ' ' + w : w; if (x.measureText(t).width <= maxW) cur = t; else { if (cur) lines.push(cur); cur = push(w); } }
    if (cur) lines.push(cur);
    if (lines.length > maxLines) { const out = lines.slice(0, maxLines); let l = out[maxLines - 1] + '…'; while (x.measureText(l).width > maxW && l.length > 1) l = l.slice(0, -2).trimEnd() + '…'; out[maxLines - 1] = l; return { lines: out, cut: true }; }
    return { lines, cut: false };
  }
  // pick the largest font size (from list) that fits within maxLines
  function fit(x, text, maxW, maxLines, sizes, fam) { for (const s of sizes) { font(x, fam(s)); const r = wrap(x, text, maxW, maxLines); if (!r.cut) return { ...r, size: s }; } const s = sizes[sizes.length - 1]; font(x, fam(s)); return { ...wrap(x, text, maxW, maxLines), size: s }; }
  function trunc(x, t, maxW) { t = String(t); if (x.measureText(t).width <= maxW) return t; while (t.length > 1 && x.measureText(t + '…').width > maxW) t = t.slice(0, -1); return t.trimEnd() + '…'; }
  function frame(x) {
    x.fillStyle = C.bg; x.fillRect(0, 0, W, H);
    let g = x.createRadialGradient(W * .2, H * .08, 0, W * .2, H * .08, W * .9); g.addColorStop(0, 'rgba(184,115,51,.14)'); g.addColorStop(1, 'rgba(184,115,51,0)'); x.fillStyle = g; x.fillRect(0, 0, W, H);
    g = x.createRadialGradient(W * .85, H * .95, 0, W * .85, H * .95, W * .8); g.addColorStop(0, 'rgba(184,115,51,.10)'); g.addColorStop(1, 'rgba(184,115,51,0)'); x.fillStyle = g; x.fillRect(0, 0, W, H);
    // star dust (deterministic)
    let s = 7; const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647;
    for (let i = 0; i < 160; i++) { x.fillStyle = `rgba(232,226,212,${.05 + rnd() * .18})`; x.beginPath(); x.arc(rnd() * W, rnd() * H, rnd() * 1.8 + .3, 0, 7); x.fill(); }
    x.strokeStyle = C.rule; x.lineWidth = 2; x.strokeRect(36, 36, W - 72, H - 72);
    // header
    if (assets.sigil) { const h = 64, w = h * assets.sigil.width / assets.sigil.height; x.drawImage(assets.sigil, PAD, 82, w, h); }
    x.fillStyle = C.amber; font(x, `500 26px ${MONO}`); spaced(x, 'ARX CORTEX · THE MEMEPLEX', 6, W - PAD, 124, 'right');
    rule(x, 176);
    // footer
    rule(x, H - 196);
    if (assets.mark) { const h = 74, w = h * assets.mark.width / assets.mark.height; x.drawImage(assets.mark, PAD, H - 160, w, h); }
    x.textAlign = 'right'; x.fillStyle = C.dim; font(x, `400 20px ${MONO}`); spaced(x, 'SEE MORE', 6, W - PAD, H - 136, 'right');
    x.fillStyle = C.bright; font(x, `500 30px ${MONO}`); spaced(x, 'arxcortex.io/memeplex', 1, W - PAD, H - 94, 'right');
  }
  function rule(x, y) { x.fillStyle = C.rule; x.fillRect(PAD, y, W - PAD * 2, 2); }
  function kicker(x, t, y) { x.fillStyle = C.amber; font(x, `500 22px ${MONO}`); spaced(x, t.toUpperCase(), 6, PAD, y); return y + 18; }
  function para(x, text, y, maxLines, sizes, color, fam) { const r = fit(x, text, W - PAD * 2, maxLines, sizes, fam || (s => `400 ${s}px ${SERIF}`)); x.fillStyle = color; x.textAlign = 'left'; const lh = r.size * 1.22; r.lines.forEach((l, i) => x.fillText(l, PAD, y + r.size + i * lh)); return mark(y + r.size + (r.lines.length - 1) * lh + r.size * .35); }
  function chips(x, list, y, maxRows, maxItems) {
    const h = 48, gap = 12, maxW = W - PAD * 2, extra = maxItems && list.length > maxItems ? list.length - maxItems : 0; list = extra ? list.slice(0, maxItems) : list;
    if (!list.length) { x.fillStyle = C.dim; font(x, `italic 400 30px ${SERIF}`); x.textAlign = 'left'; x.fillText('None mapped yet', PAD, y + 34); return mark(y + h); }
    font(x, `400 30px ${SERIF}`); x.textAlign = 'left';
    const wOf = t => x.measureText(t).width + 32;
    const items = list.map(t => trunc(x, t, maxW - 32 - wOf('+99 more') - gap));
    // greedy layout; if not all fit, reserve room for a "+N more" chip on the last row
    let placed = [], cx = PAD, row = 0;
    for (let i = 0; i < items.length; i++) {
      const w = wOf(items[i]); if (cx + w > PAD + maxW) { row++; cx = PAD; }
      if (row >= maxRows) break; placed.push({ t: items[i], x: cx, row, w }); cx += w + gap;
    }
    if (placed.length < items.length || extra) {
      while (placed.length) { const last = placed[placed.length - 1], more = `+${items.length - placed.length + extra} more`, mx = last.x + last.w + gap;
        if (last.row === maxRows - 1 && mx + wOf(more) > PAD + maxW) { placed.pop(); continue; }
        placed.push({ t: more, x: last.row === maxRows - 1 ? mx : PAD, row: last.row === maxRows - 1 ? last.row : last.row + 1, w: wOf(more), more: true }); break; }
      if (!placed.length) placed.push({ t: `+${items.length + extra} more`, x: PAD, row: 0, w: wOf(`+${items.length + extra} more`), more: true });
    }
    placed.forEach(c => { const cy = y + c.row * (h + gap); x.strokeStyle = c.more ? C.faint : C.rule; x.lineWidth = 2; x.strokeRect(c.x, cy, c.w, h); x.fillStyle = c.more ? C.dim : C.ink; x.fillText(c.t, c.x + 16, cy + 34); });
    return mark(y + (Math.max(...placed.map(c => c.row)) + 1) * (h + gap) - gap);
  }
  // diverging bars: rows [{label, v, v2?}]
  function bars(x, rows, y, rowH, nameA, nameB, scale) {
    const labW = 330, valW = 90, x0 = PAD + labW, trackW = W - PAD * 2 - labW - valW, mid = x0 + trackW / 2, unit = trackW / 2 / 5;
    rows.forEach((r, i) => {
      const cy = y + i * rowH + rowH / 2;
      x.fillStyle = C.ink; font(x, `400 22px ${MONO}`); x.textAlign = 'left'; x.textBaseline = 'middle'; x.fillText(trunc(x, r.label.toUpperCase(), labW - 20), PAD, cy);
      x.fillStyle = '#18151b'; x.fillRect(x0, cy - 16, trackW, 32); x.fillStyle = C.faint; x.fillRect(mid - 1, cy - 22, 2, 44);
      const draw = (v, top, h, colP, colN) => { x.fillStyle = v < 0 ? colN : colP; const w = Math.abs(v) * unit; x.fillRect(v < 0 ? mid - w : mid, top, w, h); };
      if (r.v2 === undefined) { draw(r.v, cy - 14, 28, C.bright, C.blueL); x.fillStyle = C.ink; font(x, `500 26px ${MONO}`); x.textAlign = 'right'; x.fillText((r.v > 0 ? '+' : '') + r.v, W - PAD, cy); }
      else { draw(r.v, cy - 15, 13, C.bright, C.blueL); draw(r.v2, cy + 2, 13, C.ink, '#9fc4d8'); font(x, `500 20px ${MONO}`); x.textAlign = 'right'; x.fillStyle = C.bright; x.fillText((r.v > 0 ? '+' : '') + r.v, W - PAD, cy - 11); x.fillStyle = C.ink; x.fillText((r.v2 > 0 ? '+' : '') + r.v2, W - PAD, cy + 13); }
      x.textBaseline = 'alphabetic';
    });
    // scale
    const sy = y + rows.length * rowH + 30; x.fillStyle = C.dim; font(x, `400 18px ${MONO}`);
    const sc = scale || ['−5 OPPOSES', '+5 STRONGLY ALIGNED']; x.textAlign = 'left'; x.fillText(sc[0], x0, sy); x.textAlign = 'center'; x.fillText('0', mid, sy); x.textAlign = 'right'; x.fillText(sc[1], x0 + trackW, sy);
    return mark(sy + 10);
  }
  const yr = (y, ap) => (ap ? 'c. ' : '') + (y < 0 ? `${-y} BC` : `AD ${y}`);
  const toBlob = cv => new Promise(r => cv.toBlob(r, 'image/png'));
  function canvas() { const cv = document.createElement('canvas'); cv.width = W; cv.height = H; return cv; }

  async function single(d) { low = 0; // {name, year, year_approx, place, root, rootLabel, plain, thinkers[], parents[], children[], ratings:[{label,v}]}
    await prep(); const cv = canvas(), x = cv.getContext('2d'); frame(x);
    let y = 240;
    if (d.root) { font(x, `500 22px ${MONO}`); const t = ('ROOT IDEA · ' + (d.rootLabel || '')).toUpperCase(); x.letterSpacing = '6px'; const w = Math.min(W - PAD * 2, x.measureText(t).width + 36); x.letterSpacing = '0px'; x.fillStyle = C.amber; x.fillRect(PAD, y, w, 48); x.fillStyle = C.bg; spaced(x, t, 6, PAD + 18, y + 33, 'left', w - 36); y += 72; }
    y = para(x, d.name, y - 10, 2, [104, 92, 80, 70, 60], C.ink, s => `500 ${s}px ${SERIF}`);
    x.fillStyle = C.dim; font(x, `400 26px ${MONO}`); spaced(x, (yr(d.year, d.year_approx) + (d.place ? ' · ' + d.place : '')).toUpperCase(), 5, PAD, y + 34, 'left', W - PAD * 2); y += 76;
    y = para(x, d.plain, y, 6, [46, 42, 38, 35], C.ink) + 26;
    const CH = 14 + 18 + 6 + 48 + 34; // one kicker + one chip row
    [['Key thinkers', d.thinkers], ['Came from', d.parents], ['Led to', d.children]].forEach(([k, l]) => { if (y + CH > SAFE) return; y = kicker(x, k, y + 14); y = chips(x, l || [], y + 6, 1, 3) + 34; });
    const STH = 10 + 56 + 40 + 14; // one stance bar with its scale
    if ((d.stance || []).length && y + 32 + STH <= SAFE) { y = kicker(x, 'Stance', y + 14); d.stance.forEach((r, k) => { if (y + STH > SAFE) return; y = bars(x, [r], y + (k ? 0 : 10), 56, null, null, r.ends || ['−5 OPPOSES', '+5 FAVORS']) + 14; }); y += 20; }
    const rowH = 62, n = Math.min(8, Math.floor((SAFE - (y + 32 + 10) - 40) / rowH));
    if (n >= 1) { y = kicker(x, 'Strongest scores', y + 14); bars(x, (d.ratings || []).slice(0, n), y + 10, rowH); }
    return toBlob(cv);
  }
  async function compare(d) { low = 0; // {a:{name,year,year_approx}, b:{...}, rows:[{label,v,v2}], dist, shared[], rel}
    await prep(); const cv = canvas(), x = cv.getContext('2d'); frame(x);
    let y = 236; y = kicker(x, 'Compare', y + 10) + 4;
    y = para(x, d.a.name, y, 2, [86, 76, 66, 58], C.bright, s => `500 ${s}px ${SERIF}`);
    x.fillStyle = C.dim; font(x, `400 24px ${MONO}`); spaced(x, yr(d.a.year, d.a.year_approx).toUpperCase(), 5, PAD, y + 24); y += 50;
    x.fillStyle = C.dim; font(x, `italic 400 44px ${SERIF}`); x.textAlign = 'left'; x.fillText('versus', PAD, y + 40); y += 54;
    y = para(x, d.b.name, y, 2, [86, 76, 66, 58], C.ink, s => `500 ${s}px ${SERIF}`);
    x.fillStyle = C.dim; font(x, `400 24px ${MONO}`); spaced(x, yr(d.b.year, d.b.year_approx).toUpperCase(), 5, PAD, y + 24); y += 64;
    // distance block
    x.strokeStyle = C.rule; x.lineWidth = 2; x.strokeRect(PAD, y, W - PAD * 2, 120);
    x.fillStyle = C.bright; font(x, `500 72px ${SERIF}`); x.textAlign = 'left'; x.fillText(d.dist, PAD + 30, y + 84);
    const dw = x.measureText(d.dist).width; x.fillStyle = C.dim; font(x, `400 28px ${SERIF}`);
    const r = wrap(x, 'score gap: 0 means identical scores; bigger means less alike', W - PAD * 2 - dw - 90, 2); r.lines.forEach((l, i) => x.fillText(l, PAD + 60 + dw, y + 52 + i * 34)); y += 160;
    // key
    font(x, `400 22px ${MONO}`); x.fillStyle = C.bright; x.fillRect(PAD, y, 40, 12); x.fillStyle = C.dim; x.fillText(trunc(x, d.a.name.toUpperCase(), 380), PAD + 54, y + 13);
    x.fillStyle = C.ink; x.fillRect(PAD + 480, y, 40, 12); x.fillStyle = C.dim; x.fillText(trunc(x, d.b.name.toUpperCase(), 380), PAD + 534, y + 13); y += 40;
    const SH = 14 + 18 + 6 + 48 + 8; // shared-ancestors block: kicker + one row (at most 2 chips + "+N more")
    const STH = 10 + 60 + 40 + 12, rowH = 66, budget = SAFE - SH - 30;
    y = kicker(x, 'Biggest differences', y + 14);
    let stance = d.stance || []; while (stance.length && y + 32 + stance.length * STH + 18 + 10 + rowH + 40 > budget) stance = stance.slice(0, -1); // keep at least one score row
    if (stance.length) { y = kicker(x, 'Stance', y + 14); stance.forEach((r, k) => { y = bars(x, [r], y + (k ? 0 : 10), 60, null, null, r.ends || ['−5 OPPOSES', '+5 FAVORS']) + 12; }); y += 18; }
    const n = Math.min(6, Math.floor((budget - (y + 10) - 40) / rowH));
    if (n >= 1) y = bars(x, d.rows.slice(0, n), y + 10, rowH) + 30;
    if (y + SH <= SAFE) { y = kicker(x, 'Shared ancestors', y + 14);
      if (d.rel && !d.shared.length) { para(x, d.rel, y, 1, [32, 28], C.dim, s => `italic 400 ${s}px ${SERIF}`); }
      else chips(x, d.shared, y + 6, 1, 2); }
    return toBlob(cv);
  }

  // preview modal
  let modal;
  function open(blob, filename) {
    const url = URL.createObjectURL(blob);
    if (!modal) {
      modal = document.createElement('div'); modal.id = 'sharecard';
      modal.innerHTML = `<div class="sc-card" role="dialog" aria-modal="true" aria-label="Share card preview"><img alt="Share card preview"><div class="sc-row"><button class="sc-share" type="button">Share</button><a class="sc-dl" download>Download PNG</a><button class="sc-x" type="button">Close</button></div></div>`;
      const st = document.createElement('style'); st.textContent = `#sharecard{position:fixed;inset:0;z-index:60;background:rgba(6,6,8,.88);display:grid;place-items:center;padding:16px}#sharecard .sc-card{display:flex;flex-direction:column;align-items:center;gap:14px;max-height:100%}#sharecard img{max-height:calc(100vh - 110px);max-width:92vw;aspect-ratio:9/16;border:1px solid #4a2810;background:#0a0a0c}#sharecard .sc-row{display:flex;gap:10px}#sharecard button,#sharecard a{font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:.18em;text-transform:uppercase;padding:10px 14px;border:1px solid #b87333;color:#b87333;background:transparent;text-decoration:none;cursor:pointer}#sharecard .sc-dl{background:#b87333;color:#0a0a0c}`;
      document.head.append(st); document.body.append(modal);
      const close = () => { modal.style.display = 'none'; };
      modal.querySelector('.sc-x').onclick = close; modal.addEventListener('click', e => { if (e.target === modal) close(); });
      addEventListener('keydown', e => { if (e.key === 'Escape' && modal.style.display !== 'none') { e.stopImmediatePropagation(); close(); } }, true);
    }
    const prev = modal.dataset.url; if (prev) URL.revokeObjectURL(prev); modal.dataset.url = url;
    modal.querySelector('img').src = url; const a = modal.querySelector('.sc-dl'); a.href = url; a.download = filename;
    const file = new File([blob], filename, { type: 'image/png' }); const sb = modal.querySelector('.sc-share');
    const can = navigator.canShare && navigator.canShare({ files: [file] }); sb.style.display = can ? '' : 'none';
    sb.onclick = () => navigator.share({ files: [file], title: 'The Memeplex · Arx Cortex', text: 'See more: arxcortex.io/memeplex' }).catch(() => {});
    modal.style.display = 'grid'; a.focus();
  }
  window.ArxShareCard = { single, compare, open, W, H, SAFE, get lastBottom() { return low; } };
})();
