/* LÚMINA | Álgebra Studio — interfaz, gráfico y conexión con Python */
'use strict';
const $ = id => document.getElementById(id), inputs = ['a', 'b', 'c', 'd', 'e', 'h'];
const presets = { sustitucion: { values: [3, -1, 7, 1, 2, 4], method: 'sustitucion' }, igualacion: { values: [5, 2, 16, 1, -1, 1], method: 'igualacion' } };
let method = 'sustitucion', latest = null, dimension = 2, revision = 0, operation = 'system', exercise = '';
const matrixInputs = Array.from({length:9}, (_,i) => 'm'+i);
const sarrusPresets = {a:[3,2,1,5,-2,-3,-2,4,4], b:[-1,2,0,0,1,-2,3,5,3], c:[4,1,2,3,0,1,2,-1,4], d:[1,2,0,-1,-3,-2,0,4,1], e:[1,1,2,3,0,1,2,1,0], f:[-1,3,-2,0,-1,2,1,4,2], g:[1,2,3,2,4,6,-1,-2,5], h:[0,1,-5,0,2,-7,0,3,6]};
const inputs3 = Array.from({ length: 12 }, (_, i) => 'v' + i);
const activeInputs = () => operation === 'determinant' ? matrixInputs : dimension === 3 ? inputs3 : inputs;
const actionLabel = () => operation === 'determinant' ? 'Calcular determinante' : 'Resolver sistema';
function escapeHTML(v) { return String(v).replace(/[&<>"']/g, s => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[s])); }
function niceNumber(s) {
  const raw = String(s).trim().replace(',', '.').replaceAll('−', '-');
  if (/^[-+]?\d+\/\d+$/.test(raw)) {
    const [num, den] = raw.split('/').map(Number);
    return den === 0 ? null : num / den;
  }
  if (!/^[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?$/.test(raw)) return null;
  const value = Number(raw);
  return Number.isFinite(value) ? value : null;
}
function signTerm(n, variable, isFirst) { if (n === null) return '?' + variable; if (n === 0) return ''; let value = Math.abs(n) === 1 ? '' : Math.abs(n); return (n < 0 ? '−' : isFirst ? '' : '+') + value + variable }
function prettyEquation(i, j, k) { let a = niceNumber($(i).value), b = niceNumber($(j).value), c = $(k).value; let bits = []; if (a !== 0) bits.push(signTerm(a, 'x', true)); if (b !== 0) bits.push(signTerm(b, 'y', !bits.length)); return (bits.join(' ').replace(/\+ −/g, '− ') || '0') + ' = ' + String(c || '?').replaceAll('-', '−') }
function preview() { if (operation === 'determinant') { $('equation-preview').textContent = 'Matriz A de orden 3 · nueve entradas por filas · det(A) = S↘ − S↗'; return; } if (dimension === 3) { $('equation-preview').textContent = 'ax + by + cz = d · Introduce enteros, decimales o fracciones en cada fila.'; return; } $('equation-preview').innerHTML = '<span>' + escapeHTML(prettyEquation('a', 'b', 'c')) + '</span><span>' + escapeHTML(prettyEquation('d', 'e', 'h')) + '</span>'; }
function selectMethod(name) { if (operation !== 'system' || dimension !== 2 || !['sustitucion', 'igualacion', 'reduccion', 'cramer'].includes(name)) return; method = name; document.querySelectorAll('#methods2 .method').forEach(b => b.classList.toggle('selected', b.dataset.method === name)); clearResults(); }
function loadPreset(name) { let p = presets[name]; if (!p) return; if (dimension !== 2 || operation !== 'system') setDimension(2); inputs.forEach((id, i) => $(id).value = p.values[i]); selectMethod(p.method); document.querySelectorAll('.preset').forEach(el => el.classList.toggle('active', el.id === 'preset-' + name)); preview(); runSolve(); }
function clearResults() {
  latest = null; revision += 1;
  $('print-heading').textContent = 'LÚMINA · ' + (operation === 'determinant' ? 'Determinante 3×3 · Sarrus' : 'Sistema ' + dimension + '×' + dimension);
  $('solution').innerHTML = '<div class="solution-head"><strong>Tu resultado aparecerá aquí</strong><span class="pill">● Preparado</span></div><p class="solution-description">Completa los campos del sistema y presiona «Resolver sistema».</p>';
  $('steps').innerHTML = '<div class="empty">El procedimiento aparecerá al resolver el sistema.</div>';
  $('checks').innerHTML = '<div class="empty">No hay un resultado para comprobar.</div>';
  $('graph').innerHTML = '';
  $('matrix-view').innerHTML = '<div class="empty">A · (x, y, z)ᵀ = b. Resuelve para explorar D, Dx, Dy y Dz.</div>';
  $('feedback').textContent = '';
  $('graph-note').textContent = 'Las rectas se mostrarán cuando resuelvas un sistema.';
  if (operation === 'determinant') {
    $('solution').innerHTML = '<div class="empty">Completa la matriz y pulsa «Calcular determinante».</div>';
    $('matrix-view').innerHTML = '<div class="empty">La matriz ampliada y sus seis diagonales aparecerán al calcular.</div>';
  }
}
function resetInputs() {
  activeInputs().forEach(id => $(id).value = '');
  document.querySelectorAll('.preset').forEach(el => el.classList.remove('active'));
  preview(); clearResults();
  $('feedback').textContent = 'Introduce un sistema para continuar.';
}
function showSolution(data) {
  if (data.operation === 'determinant') { showDeterminant(data); return; }
  if (data.dimension === 3) { showSolution3(data); return; }
  let root = $('solution'); let r = data.result; if (data.status === 'unique') root.innerHTML = '<div class="solution-head"><strong>✧ ' + escapeHTML(data.headline) + '</strong><span class="pill">✓ Verificada</span></div><div class="solution-grid"><div class="solution-val"><small>VARIABLE X</small><div class="exact">x = ' + escapeHTML(r.x) + '</div><div class="approx">≈ ' + escapeHTML(r.xDecimal) + '</div></div><div class="solution-val"><small>VARIABLE Y</small><div class="exact">y = ' + escapeHTML(r.y) + '</div><div class="approx">≈ ' + escapeHTML(r.yDecimal) + '</div></div></div><div class="solution-description">Coordenada de intersección: (' + escapeHTML(r.x) + ', ' + escapeHTML(r.y) + ')</div>';
  else root.innerHTML = '<div class="solution-head"><strong>' + escapeHTML(data.headline) + '</strong><span class="pill warn">⚠ Caso especial</span></div><div class="solution-description" style="font-size:13px;line-height:1.7">' + escapeHTML(data.explanation) + '</div>';
}
function showSteps(data) {
  $('method-caption').textContent = 'Método de ' + data.methodLabel.toLowerCase() + ' · explicación ordenada'; $('steps').innerHTML = data.steps.map((s, i) => '<div class="step-card"><div class="step-index">' + (i + 1) + '</div><div><div class="step-title">' + escapeHTML(s.title) + '</div>' + s.lines.map(l => '<div class="mathline">' + escapeHTML(l) + '</div>').join('') + '<p class="step-note">' + escapeHTML(s.note) + '</p></div></div>').join('');
  $('checks').innerHTML = data.checks.length ? data.checks.map(c => '<div class="check-row"><span class="check-icon">✓</span><div><strong>' + escapeHTML(c.equation) + ' · Se cumple</strong><small>' + escapeHTML(c.detail) + ' &nbsp; (resultado esperado: ' + escapeHTML(c.expected) + ')</small></div></div>').join('') : '<div class="empty">No hay una solución única para comprobar; consulta la clasificación en el procedimiento.</div>';
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
async function runSolve() {
  const btn = $('solve-btn'), requestedRevision = revision;
  $('feedback').textContent = ''; btn.disabled = true; btn.innerHTML = '✧ Calculando…';
  try {
    const values = activeInputs().map(id => $(id).value);
    if (![2, 3].includes(dimension) || (operation === 'determinant' ? method !== 'sarrus' : dimension === 3 ? method !== 'cramer3' : !['sustitucion', 'igualacion', 'reduccion', 'cramer'].includes(method))) throw new Error('Selecciona una dimensión y un método válidos.');
    for (let i = 0; i < values.length; i++) {
      if (values[i].trim().length > 32 || niceNumber(values[i].replaceAll('−', '-')) === null) { $(activeInputs()[i]).focus(); throw new Error('Completa todos los coeficientes con números válidos. Usa 3, -2, 0.5 o 3/4; el denominador no puede ser cero.'); }
    }
    let response = await fetch('/api/solve', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ operation, dimension, method, values }) });
    let data = await response.json();
    if (revision !== requestedRevision) return;
    if (!response.ok || !data.ok) throw new Error(data.error || 'No se pudo resolver el sistema.');
    latest = data; if (exercise && operation === 'determinant') data.exercise = exercise; showSolution(data); showSteps(data);
    $('print-heading').textContent = 'LÚMINA · ' + (operation === 'determinant' ? 'Determinante 3×3' + (exercise ? ' · Ejercicio '+exercise+')' : '') : 'Sistema '+dimension+'×'+dimension) + ' · ' + data.methodLabel + ' · ' + data.equations.join('; ');
    if (operation === 'determinant') renderSarrus(data); else if (dimension === 3) renderMatrices(data); else renderGraph(data);
  } catch (err) { if (revision === requestedRevision) $('feedback').textContent = err.message || 'Se produjo un error.'; }
  finally { btn.disabled = false; btn.innerHTML = '<span>✧</span> ' + actionLabel() + ' <span>→</span>'; }
}
function buildReport() { if (!latest) { $('feedback').textContent = 'Calcula un resultado antes de exportar.'; return null; } const d = latest; if (d.operation === 'determinant') return determinantReport(d); let content = ['LÚMINA | ÁLGEBRA STUDIO', 'PROCEDIMIENTO DE ECUACIONES LINEALES ' + (d.dimension || 2) + '×' + (d.dimension || 2), 'Fecha: ' + new Date().toLocaleString('es-CO'), '', 'Método: ' + d.methodLabel, 'Sistema original:', ...d.equations, '', 'Resultado: ' + d.headline]; if (d.result) content.push('x = ' + d.result.x + ' ≈ ' + d.result.xDecimal, 'y = ' + d.result.y + ' ≈ ' + d.result.yDecimal); if (d.result && d.dimension === 3) content.push('z = ' + d.result.z + ' ≈ ' + d.result.zDecimal); content.push(d.explanation, '', 'PROCEDIMIENTO'); d.steps.forEach((s, i) => content.push('', (i + 1) + '. ' + s.title, ...s.lines, s.note)); content.push('', 'COMPROBACIÓN'); d.checks.forEach(c => content.push(c.equation + ': ' + c.detail + '; esperado ' + c.expected + ' → ' + (c.pass ? 'Correcto' : 'Revisar'))); return content.join('\n'); }
function downloadReport() { let t = buildReport(); if (!t) return; let blob = new Blob(['\ufeff', t], { type: 'text/plain;charset=utf-8' }), url = URL.createObjectURL(blob), a = document.createElement('a'); a.href = url; a.download = (latest.operation === 'determinant' ? 'Lumina_Sarrus' + (latest.exercise ? '_'+latest.exercise : '') + '_3x3.txt' : 'Lumina_Procedimiento_' + (latest.dimension || 2) + 'x' + (latest.dimension || 2) + '.txt'); a.click(); setTimeout(() => URL.revokeObjectURL(url), 500); }
function printReport() { if (!latest) { $('feedback').textContent = 'Calcula un resultado antes de generar el PDF.'; return } window.print() }
[...inputs, ...inputs3, ...matrixInputs].forEach(id => $(id).addEventListener('input', () => { exercise = ''; preview(); clearResults(); document.querySelectorAll('.preset').forEach(el => el.classList.remove('active')) })); document.addEventListener('keydown', e => { if (e.ctrlKey && e.key === 'Enter') { e.preventDefault(); runSolve() } });
function setDimension(value) {
  if (![2, 3].includes(value)) return;
  operation = 'system'; exercise = '';
  $('matrix-inputs').hidden = true; $('method-sarrus').hidden = true; $('sarrus-presets').hidden = true; $('system-presets').hidden = false;
  $('mode-sarrus').classList.remove('selected'); $('mode-sarrus').setAttribute('aria-pressed','false');
  $('input-title').textContent = 'Configura tu sistema'; $('input-kicker').textContent = '01 / ECUACIONES LINEALES'; $('check-help').textContent = '¿Funcionan los valores en cada ecuación?';
  $('solve-btn').textContent = '✧ Resolver sistema →';
  dimension = value; method = value === 3 ? 'cramer3' : 'sustitucion';
  for (const [id, visible] of [['equations2', value === 2], ['equations3', value === 3], ['methods2', value === 2], ['methods3', value === 3], ['presets2', value === 2], ['preset3', value === 3], ['graph-section', value === 2], ['matrix-view', value === 3]]) $(id).hidden = !visible;
  [2, 3].forEach(n => { $('mode' + n).classList.toggle('selected', n === value); $('mode' + n).setAttribute('aria-pressed', String(n === value)); });
  document.querySelectorAll('#methods2 .method').forEach(b => b.classList.toggle('selected', b.dataset.method === method));
  $('mode-title').textContent = 'Sistemas lineales ' + value + '×' + value;
  $('input-help').textContent = value === 3 ? 'Introduce doce coeficientes: enteros, negativos, decimales o fracciones.' : 'Introduce los seis coeficientes.';
  document.title = 'LÚMINA · Álgebra Studio · ' + value + '×' + value;
  document.querySelectorAll('#sarrus-preset-buttons .preset').forEach(b => b.classList.remove('active'));
  clearResults(); preview();
}
function loadPreset3() {
  setDimension(3);
  [2, 1, -1, 8, -3, -1, 2, -11, -2, 1, 2, -3].forEach((v, i) => $(inputs3[i]).value = v);
  preview(); runSolve();
}
function showSolution3(data) {
  $('solution').innerHTML = '<div class="solution-head"><strong>' + escapeHTML(data.headline) + '</strong><span class="pill">3×3 · Cramer</span></div>' +
    (data.result ? '<div class="solution-grid three">' + ['x', 'y', 'z'].map(v => '<div class="solution-val"><small>VARIABLE ' + v.toUpperCase() + '</small><div class="exact">' + v + ' = ' + escapeHTML(data.result[v]) + '</div><div class="approx">≈ ' + escapeHTML(data.result[v + 'Decimal']) + '</div></div>').join('') + '</div>' : '') +
    '<p class="solution-description">' + escapeHTML(data.explanation) + '</p>';
}
function renderMatrices(data) {
  $('matrix-view').innerHTML = '<h3>Matrices de Cramer · A · (x, y, z)ᵀ = b</h3><p class="solution-description">D usa los coeficientes; Dx, Dy y Dz sustituyen la columna de cada variable por b. Expansión: +, −, +.</p><div class="determinant-grid">' +
    Object.entries(data.determinants).map(([name, d]) => '<article class="determinant-card"><strong>' + name + ' = ' + escapeHTML(d.value) + '</strong><table class="matrix"><caption>Matriz de ' + name + '</caption><tbody>' + d.matrix.map(row => '<tr>' + row.map(cell => '<td>' + escapeHTML(cell) + '</td>').join('') + '</tr>').join('') + '</tbody></table></article>').join('') + '</div>';
}
function setSarrus() {
  setDimension(3); operation = 'determinant'; method = 'sarrus';
  for (const id of ['equations3','methods3','system-presets','graph-section']) $(id).hidden = true;
  for (const id of ['matrix-inputs','method-sarrus','sarrus-presets','matrix-view']) $(id).hidden = false;
  [2,3].forEach(n => { $('mode'+n).classList.remove('selected'); $('mode'+n).setAttribute('aria-pressed','false'); });
  $('mode-sarrus').classList.add('selected'); $('mode-sarrus').setAttribute('aria-pressed','true');
  $('mode-title').textContent = 'Determinantes 3×3 · Sarrus'; document.title = 'LÚMINA · Determinantes por Sarrus';
  $('input-title').textContent = 'Configura tu matriz'; $('input-kicker').textContent = '01 / MATRIZ DE ORDEN TRES';
  $('input-help').textContent = 'Introduce nueve entradas por filas. Admite enteros, negativos, decimales y fracciones.';
  $('check-help').textContent = 'Verificación independiente por expansión de cofactores.';
  $('solve-btn').textContent = '✧ Calcular determinante →';
  clearResults(); preview();
  $('matrix-view').innerHTML = '<div class="empty">Resuelve para ver la matriz ampliada, las seis diagonales y sus productos.</div>';
}
function loadSarrusPreset(name) {
  if (!Object.hasOwn(sarrusPresets,name)) return;
  setSarrus(); exercise = name;
  sarrusPresets[name].forEach((v,i) => $(matrixInputs[i]).value = v);
  document.querySelectorAll('#sarrus-preset-buttons .preset').forEach(b => b.classList.toggle('active',b.dataset.exercise===name));
  runSolve();
}
function showDeterminant(data) {
  $('solution').innerHTML = '<div class="solution-head"><strong>'+ (data.exercise ? 'Ejercicio '+escapeHTML(data.exercise)+') · ' : '') +'Determinante de A</strong><span class="pill">Sarrus</span></div><div class="determinant-result">det(A) = '+escapeHTML(data.result.determinant)+'</div><div class="approx">≈ '+escapeHTML(data.result.decimal)+'</div><p class="solution-description">'+escapeHTML(data.explanation)+'</p>';
}
function renderSarrus(data) {
  $('matrix-view').innerHTML = '<h3>Diagonales de Sarrus</h3><p class="solution-description">Repetimos las columnas 1 y 2 a la derecha. Pulsa un producto para resaltar sus tres factores: ↘ se suma, ↗ se resta.</p><div class="sarrus-matrix-wrap"><table class="matrix sarrus-matrix"><caption>A con sus dos primeras columnas repetidas</caption><tbody>'+data.extendedMatrix.map((row,r) => '<tr>'+row.map((v,c) => '<td data-cell="'+r+'-'+c+'" class="'+(c>=3?'repeated':'')+'">'+escapeHTML(v)+'</td>').join('')+'</tr>').join('')+'</tbody></table></div><div class="diagonal-products">'+data.products.map((item,i) => '<button type="button" class="diagonal-product '+item.direction+'" aria-pressed="false" onclick="highlightDiagonal('+i+')"><strong>'+(i<3?'↘ ':'↗ ')+item.name+'</strong><span>'+escapeHTML(item.formula)+' = '+escapeHTML(item.value)+'</span></button>').join('')+'</div><div class="sarrus-summary">S↘ = '+escapeHTML(data.sums.down)+' · S↗ = '+escapeHTML(data.sums.up)+'<br><strong>det(A) = ('+escapeHTML(data.sums.down)+') − ('+escapeHTML(data.sums.up)+') = '+escapeHTML(data.result.determinant)+'</strong></div>';
}
function highlightDiagonal(index) {
  if (!latest || latest.operation !== 'determinant' || !latest.products[index]) return;
  const item = latest.products[index];
  document.querySelectorAll('.sarrus-matrix td').forEach(cell => { cell.classList.remove('diagonal-down','diagonal-up'); if(item.path.some(([r,c]) => cell.dataset.cell===r+'-'+c)) cell.classList.add('diagonal-'+item.direction); });
  document.querySelectorAll('.diagonal-product').forEach((b,i) => b.setAttribute('aria-pressed',String(i===index)));
}
function determinantReport(d) {
  const lines = ['LÚMINA | ÁLGEBRA STUDIO', 'DETERMINANTE 3×3 · REGLA DE SARRUS', d.exercise ? 'Ejercicio '+d.exercise+')' : 'Matriz personalizada', 'Fecha: '+new Date().toLocaleString('es-CO'), '', 'Matriz A:', ...d.equations, '', 'det(A) = '+d.result.determinant+' ≈ '+d.result.decimal, d.explanation];
  d.steps.forEach((s,i) => lines.push('', (i+1)+'. '+s.title, ...s.lines, s.note));
  lines.push('', 'COMPROBACIÓN'); d.checks.forEach(c => lines.push(c.equation+': '+c.detail+' → '+(c.pass?'Correcto':'Revisar')));
  return lines.join('\n');
}
$('sarrus-preset-buttons').innerHTML = Object.keys(sarrusPresets).map(name => '<button type="button" class="preset" data-exercise="'+name+'" onclick="loadSarrusPreset(\''+name+'\')"><strong>'+name+')</strong><small>'+sarrusPresets[name].slice(0,3).join(' · ')+'</small></button>').join('');
preview(); runSolve();
