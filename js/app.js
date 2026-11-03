/* LÚMINA | Álgebra Studio — interfaz, gráfico y conexión con Python */
'use strict';
const $ = id => document.getElementById(id), inputs = ['a', 'b', 'c', 'd', 'e', 'h'];
const presets = { sustitucion: { values: [3, -1, 7, 1, 2, 4], method: 'sustitucion' }, igualacion: { values: [5, 2, 16, 1, -1, 1], method: 'igualacion' } };
let method = 'sustitucion', latest = null;
function escapeHTML(v) { return String(v).replace(/[&<>"']/g, s => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[s])); }
function niceNumber(s) { let raw = String(s).trim().replace(',', '.'); if (/^[-+]?\d+\/[-+]?\d+$/.test(raw)) { let parts = raw.split('/'); let den = Number(parts[1]); return den === 0 ? null : Number(parts[0]) / den; } let n = Number(raw); return raw !== '' && Number.isFinite(n) ? n : null }
function signTerm(n, variable, isFirst) { if (n === null) return '?' + variable; if (n === 0) return ''; let value = Math.abs(n) === 1 ? '' : Math.abs(n); return (n < 0 ? '−' : isFirst ? '' : '+') + value + variable }
function prettyEquation(i, j, k) { let a = niceNumber($(i).value), b = niceNumber($(j).value), c = $(k).value; let bits = []; if (a !== 0) bits.push(signTerm(a, 'x', true)); if (b !== 0) bits.push(signTerm(b, 'y', !bits.length)); return (bits.join(' ').replace(/\+ −/g, '− ') || '0') + ' = ' + String(c || '?').replaceAll('-', '−') }
function preview() { $('equation-preview').innerHTML = '<span>' + escapeHTML(prettyEquation('a', 'b', 'c')) + '</span><span>' + escapeHTML(prettyEquation('d', 'e', 'h')) + '</span>'; }
function selectMethod(name) { method = name; document.querySelectorAll('.method').forEach(b => b.classList.toggle('selected', b.dataset.method === name)); clearResults(); }
function loadPreset(name) { let p = presets[name]; if (!p) return; inputs.forEach((id, i) => $(id).value = p.values[i]); selectMethod(p.method); document.querySelectorAll('.preset').forEach(el => el.classList.toggle('active', el.id === 'preset-' + name)); preview(); runSolve(); }
function clearResults() {
  latest = null;
  $('solution').innerHTML = '<div class="solution-head"><strong>Tu resultado aparecerá aquí</strong><span class="pill">● Preparado</span></div><p class="solution-description">Completa los seis campos y presiona «Resolver sistema».</p>';
  $('steps').innerHTML = '<div class="empty">El procedimiento aparecerá al resolver el sistema.</div>';
  $('checks').innerHTML = '<div class="empty">No hay un resultado para comprobar.</div>';
  $('graph').innerHTML = '';
  $('graph-note').textContent = 'Las rectas se mostrarán cuando resuelvas un sistema.';
}
function resetInputs() {
  inputs.forEach(id => $(id).value = '');
  document.querySelectorAll('.preset').forEach(el => el.classList.remove('active'));
  preview(); clearResults();
  $('feedback').textContent = 'Introduce un sistema para continuar.';
}
function showSolution(data) {
  let root = $('solution'); let r = data.result; if (data.status === 'unique') root.innerHTML = '<div class="solution-head"><strong>✧ ' + escapeHTML(data.headline) + '</strong><span class="pill">✓ Verificada</span></div><div class="solution-grid"><div class="solution-val"><small>VARIABLE X</small><div class="exact">x = ' + escapeHTML(r.x) + '</div><div class="approx">≈ ' + escapeHTML(r.xDecimal) + '</div></div><div class="solution-val"><small>VARIABLE Y</small><div class="exact">y = ' + escapeHTML(r.y) + '</div><div class="approx">≈ ' + escapeHTML(r.yDecimal) + '</div></div></div><div class="solution-description">Coordenada de intersección: (' + escapeHTML(r.x) + ', ' + escapeHTML(r.y) + ')</div>';
  else root.innerHTML = '<div class="solution-head"><strong>' + escapeHTML(data.headline) + '</strong><span class="pill warn">⚠ Caso especial</span></div><div class="solution-description" style="font-size:13px;line-height:1.7">' + escapeHTML(data.explanation) + '</div>';
}
function showSteps(data) {
  $('method-caption').textContent = 'Método de ' + data.methodLabel.toLowerCase() + ' · explicación ordenada'; $('steps').innerHTML = data.steps.map((s, i) => '<div class="step-card"><div class="step-index">' + (i + 1) + '</div><div><div class="step-title">' + escapeHTML(s.title) + '</div>' + s.lines.map(l => '<div class="mathline">' + escapeHTML(l) + '</div>').join('') + '<p class="step-note">' + escapeHTML(s.note) + '</p></div></div>').join('');
  $('checks').innerHTML = data.checks.length ? data.checks.map(c => '<div class="check-row"><span class="check-icon">✓</span><div><strong>' + escapeHTML(c.equation) + ' · Se cumple</strong><small>' + escapeHTML(c.detail) + ' &nbsp; (resultado esperado: ' + escapeHTML(c.expected) + ')</small></div></div>').join('') : '<div class="empty">No hay una pareja única de valores para comprobar.</div>';
}
function renderGraph(data) {
  const svg = $('graph'), W = 720, H = 350, L = 48, R = 20, T = 20, B = 33; let cx = 0, cy = 0; if (data.result) { cx = data.result.xNumber; cy = data.result.yNumber; } let halfX = Math.max(4, Math.ceil(Math.abs(cx) * .3 + 3)), halfY = Math.max(4, Math.ceil(Math.abs(cy) * .3 + 3)); let minX = cx - halfX, maxX = cx + halfX, minY = cy - halfY, maxY = cy + halfY; let sx = x => L + (x - minX) * (W - L - R) / (maxX - minX); let sy = y => H - B - (y - minY) * (H - T - B) / (maxY - minY);
  let o = '<defs><clipPath id="plotClip"><rect x="' + L + '" y="' + T + '" width="' + (W - L - R) + '" height="' + (H - T - B) + '" rx="4"/></clipPath></defs>';
  const gapX = Math.max(1, Math.ceil((maxX - minX) / 12)), gapY = Math.max(1, Math.ceil((maxY - minY) / 8));
  for (let x = Math.ceil(minX / gapX) * gapX; x <= maxX; x += gapX) { let p = sx(x); o += '<line x1="' + p + '" y1="' + T + '" x2="' + p + '" y2="' + (H - B) + '" stroke="#f1edf6" stroke-width="1"/><text x="' + p + '" y="' + (H - 12) + '" text-anchor="middle">' + x.toFixed(x % 1 ? 1 : 0) + '</text>' }
  for (let y = Math.ceil(minY / gapY) * gapY; y <= maxY; y += gapY) { let p = sy(y); o += '<line x1="' + L + '" y1="' + p + '" x2="' + (W - R) + '" y2="' + p + '" stroke="#f1edf6" stroke-width="1"/><text x="' + (L - 9) + '" y="' + (p + 4) + '" text-anchor="end">' + y.toFixed(y % 1 ? 1 : 0) + '</text>' }
  if (minY <= 0 && maxY >= 0) o += '<line x1="' + L + '" y1="' + sy(0) + '" x2="' + (W - R) + '" y2="' + sy(0) + '" stroke="#cfc6db" stroke-width="1.5"/>';
  if (minX <= 0 && maxX >= 0) o += '<line x1="' + sx(0) + '" y1="' + T + '" x2="' + sx(0) + '" y2="' + (H - B) + '" stroke="#cfc6db" stroke-width="1.5"/>';
  let [a, b, c, d, e, h] = data.coefficients;
  function line(a, b, c, cl) { if (b !== 0) { let y1 = (c - a * minX) / b, y2 = (c - a * maxX) / b; return '<line x1="' + sx(minX) + '" y1="' + sy(y1) + '" x2="' + sx(maxX) + '" y2="' + sy(y2) + '" stroke="' + cl + '" stroke-width="3.5" stroke-linecap="round"/>' } if (a !== 0) { let x = c / a; return '<line x1="' + sx(x) + '" y1="' + sy(minY) + '" x2="' + sx(x) + '" y2="' + sy(maxY) + '" stroke="' + cl + '" stroke-width="3.5"/>' } return ''; }
  o += '<g clip-path="url(#plotClip)">' + line(a, b, c, '#9066bc') + line(d, e, h, '#e481a6') + '</g>';
  if (data.result) { let x = sx(cx), y = sy(cy); o += '<line x1="' + x + '" x2="' + x + '" y1="' + y + '" y2="' + (H - B) + '" stroke="#bda9d4" stroke-dasharray="5 5"/><line x1="' + L + '" x2="' + x + '" y1="' + y + '" y2="' + y + '" stroke="#bda9d4" stroke-dasharray="5 5"/><circle cx="' + x + '" cy="' + y + '" r="12" fill="#7751b533"/><circle cx="' + x + '" cy="' + y + '" r="5" fill="#6e4ba7" stroke="white" stroke-width="2"/><rect x="' + Math.min(W - 168, x + 14) + '" y="' + Math.max(T + 5, y - 33) + '" width="145" height="24" rx="8" fill="#f2eafa" stroke="#e4d6f0"/><text class="plot-tag" x="' + Math.min(W - 158, x + 23) + '" y="' + Math.max(T + 21, y - 17) + '">(' + Number(cx).toFixed(2) + ', ' + Number(cy).toFixed(2) + ')</text>' }
  svg.innerHTML = o; $('graph-note').textContent = data.status === 'unique' ? 'El punto marcado representa la solución común de ambas ecuaciones.' : data.explanation;
}
async function runSolve() { const btn = $('solve-btn'); $('feedback').textContent = ''; btn.disabled = true; btn.innerHTML = '✧ Calculando…'; try { let response = await fetch('/api/solve', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ method, values: inputs.map(id => $(id).value) }) }); let data = await response.json(); if (!response.ok || !data.ok) throw new Error(data.error || 'No se pudo resolver el sistema.'); latest = data; showSolution(data); showSteps(data); renderGraph(data); } catch (err) { $('feedback').textContent = err.message || 'Se produjo un error.'; } finally { btn.disabled = false; btn.innerHTML = '<span>✧</span> Resolver sistema <span style="font-size:18px">→</span>'; } }
function buildReport() { if (!latest) { $('feedback').textContent = 'Resuelve un sistema antes de exportar.'; return null; } const d = latest; let content = ['LÚMINA | ÁLGEBRA STUDIO', 'PROCEDIMIENTO DE ECUACIONES LINEALES 2×2', 'Fecha: ' + new Date().toLocaleString('es-CO'), '', 'Método: ' + d.methodLabel, 'Sistema original:', ...d.equations, '', 'Resultado: ' + d.headline]; if (d.result) content.push('x = ' + d.result.x + ' ≈ ' + d.result.xDecimal, 'y = ' + d.result.y + ' ≈ ' + d.result.yDecimal); content.push('', 'PROCEDIMIENTO'); d.steps.forEach((s, i) => content.push('', (i + 1) + '. ' + s.title, ...s.lines, s.note)); content.push('', 'COMPROBACIÓN'); d.checks.forEach(c => content.push(c.equation + ': ' + c.detail + '; esperado ' + c.expected + ' → ' + (c.pass ? 'Correcto' : 'Revisar'))); return content.join('\n'); }
function downloadReport() { let t = buildReport(); if (!t) return; let blob = new Blob(['\ufeff', t], { type: 'text/plain;charset=utf-8' }), url = URL.createObjectURL(blob), a = document.createElement('a'); a.href = url; a.download = 'Lumina_Procedimiento_2x2.txt'; a.click(); setTimeout(() => URL.revokeObjectURL(url), 500); }
function printReport() { if (!latest) { $('feedback').textContent = 'Resuelve un sistema antes de generar el PDF.'; return } window.print() }
inputs.forEach(id => $(id).addEventListener('input', () => { preview(); clearResults(); document.querySelectorAll('.preset').forEach(el => el.classList.remove('active')) })); document.addEventListener('keydown', e => { if (e.ctrlKey && e.key === 'Enter') { e.preventDefault(); runSolve() } });
preview(); runSolve();
