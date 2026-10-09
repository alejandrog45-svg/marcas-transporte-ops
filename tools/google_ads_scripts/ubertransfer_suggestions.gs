/**
 * UberTransfer · recomendaciones de campaña (solo lectura)
 *
 * Ejecutar main() desde Google Ads Scripts. Este script NO crea, modifica,
 * pausa ni publica campañas. Solo consulta AdsApp.report() y guarda el
 * resultado de las recomendaciones en Firestore para que el panel lo lea.
 *
 * Antes de activarlo, configurar FIRESTORE_PROJECT_ID y revisar el documento
 * docs/ads/google_ads_script_setup.md.
 */
var FIRESTORE_PROJECT_ID = 'ubertransfer-ops';
var FIRESTORE_DOCUMENT = 'panel/aiSuggestions';
var LOOKBACK = 'LAST_30_DAYS';

function main() {
  var account = AdsApp.currentAccount();
  var campaignRows = reportRows(
    'SELECT campaign.id, campaign.name, campaign.status, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions, metrics.ctr ' +
    'FROM campaign WHERE segments.date DURING ' + LOOKBACK + ' ORDER BY metrics.clicks DESC'
  );
  var termRows = reportRows(
    'SELECT campaign.name, search_term_view.search_term, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions ' +
    'FROM search_term_view WHERE segments.date DURING ' + LOOKBACK + ' ORDER BY metrics.clicks DESC'
  );
  var deviceRows = reportRows(
    'SELECT campaign.name, segments.device, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions ' +
    'FROM campaign WHERE segments.date DURING ' + LOOKBACK + ' ORDER BY metrics.clicks DESC'
  );
  var hourRows = reportRows(
    'SELECT campaign.name, segments.hour, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions ' +
    'FROM campaign WHERE segments.date DURING ' + LOOKBACK + ' ORDER BY metrics.clicks DESC'
  );
  var geoRows = reportRows(
    'SELECT campaign.name, geographic_view.country_criterion_id, geographic_view.location_type, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions ' +
    'FROM geographic_view WHERE segments.date DURING ' + LOOKBACK + ' ORDER BY metrics.clicks DESC'
  );

  var suggestions = buildSuggestions(campaignRows, termRows, deviceRows, hourRows, geoRows);
  writeFirestore({
    source: 'Google Ads Scripts · AdsApp.report() · solo lectura',
    accountId: account.getCustomerId(),
    period: LOOKBACK,
    updatedAt: new Date().toISOString(),
    suggestions: suggestions,
    queryStatus: { campaigns: campaignRows.ok, terms: termRows.ok, devices: deviceRows.ok, hours: hourRows.ok, regions: geoRows.ok },
    queryErrors: [campaignRows, termRows, deviceRows, hourRows, geoRows].filter(function (r) { return !r.ok; }).map(function (r) { return r.error; })
  });
}

function reportRows(query) {
  try {
    var rows = [];
    var it = AdsApp.report(query).rows();
    while (it.hasNext()) rows.push(it.next());
    return { ok: true, rows: rows };
  } catch (e) {
    return { ok: false, rows: [], error: String(e) };
  }
}

function n(v) { return Number(v || 0); }
function cost(v) { return n(v) / 1000000; }
function nameOf(r, keys) { for (var i = 0; i < keys.length; i++) if (r[keys[i]]) return String(r[keys[i]]); return 'sin dato'; }
function top(rows, field) { return rows.rows.slice().sort(function (a, b) { return n(b[field]) - n(a[field]); })[0]; }
function evidence(text, date, campaign, reason, confidence, confirm) {
  return { evidence: text, date: date, campaign: campaign || 'sin campaña identificada', reason: reason, confidence: confidence, confirm: confirm };
}

function buildSuggestions(camps, terms, devices, hours, regions) {
  var date = new Date().toISOString();
  var campaign = camps.rows.length ? nameOf(camps.rows[0], ['campaign.name']) : 'sin campaña identificada';
  var out = [];
  var bestTerm = top(terms, 'metrics.clicks');
  var costly = terms.rows.filter(function (r) { return n(r['metrics.clicks']) > 0 && n(r['metrics.conversions']) === 0 && cost(r['metrics.costMicros']) > 0; }).sort(function (a, b) { return cost(b['metrics.costMicros']) - cost(a['metrics.costMicros']); })[0];
  var bestHour = top(hours, 'metrics.clicks');
  var bestRegion = top(regions, 'metrics.clicks');
  var convertingDevices = devices.rows.filter(function (r) { return n(r['metrics.conversions']) > 0; }).sort(function (a, b) { return cost(a['metrics.costMicros']) / n(a['metrics.conversions']) - cost(b['metrics.costMicros']) / n(b['metrics.conversions']); });

  out.push({ title: 'Crear campaña basada en la actual', action: 'Preparar un borrador manual a partir de la campaña observada.', kind: 'PROPUESTA', data: evidence('Campañas consultadas: ' + camps.rows.length + '; fuente AdsApp.report()', date, campaign, 'Existe una estructura real que puede revisarse antes de copiar.', camps.rows.length ? 'Media' : 'Baja', 'Objetivo, presupuesto, ubicaciones y conversiones.') });
  out.push({ title: 'Duplicar estructura con cambios sugeridos', action: 'Copiar manualmente solo los elementos aprobados.', kind: 'PROPUESTA', data: evidence('Campañas, términos y métricas de los últimos 30 días.', date, campaign, 'Permite comparar sin modificar la campaña original.', camps.rows.length ? 'Media' : 'Baja', 'Qué grupos, anuncios y estrategia se duplican.') });
  out.push({ title: 'Reforzar regiones de mejor rendimiento', action: bestRegion ? 'Revisar el criterio geográfico con más clics.' : 'Esperar un desglose geográfico válido.', kind: bestRegion ? 'UBICACIÓN REAL' : 'DATOS INSUFICIENTES', data: evidence(bestRegion ? 'Criterio ' + nameOf(bestRegion, ['geographic_view.location_type']) + ': ' + n(bestRegion['metrics.clicks']) + ' clics.' : 'AdsApp.report() no devolvió filas geográficas utilizables.', date, campaign, bestRegion ? 'Concentró más clics entre los criterios recibidos.' : 'No se inventan regiones.', bestRegion ? 'Media' : 'Baja', 'Zonas que realmente atiende el negocio.') });
  out.push({ title: 'Ajustar horarios', action: bestHour ? 'Evaluar manualmente el horario con mayor actividad.' : 'No ajustar hasta recibir filas horarias.', kind: bestHour ? 'HORARIO REAL' : 'DATOS INSUFICIENTES', data: evidence(bestHour ? 'Hora ' + nameOf(bestHour, ['segments.hour']) + ': ' + n(bestHour['metrics.clicks']) + ' clics.' : 'AdsApp.report() no devolvió actividad horaria utilizable.', date, campaign, bestHour ? 'Es la hora con más clics observados.' : 'No se rellenan horas con ceros inventados.', bestHour ? 'Media' : 'Baja', 'Horario real de atención y zona horaria.') });
  out.push({ title: 'Agregar palabras de alto rendimiento', action: bestTerm ? 'Revisar si el término con más clics debe incorporarse con concordancia controlada.' : 'No agregar términos sin evidencia.', kind: bestTerm ? 'TÉRMINO REAL' : 'DATOS INSUFICIENTES', data: evidence(bestTerm ? '«' + nameOf(bestTerm, ['search_term_view.search_term']) + '»: ' + n(bestTerm['metrics.clicks']) + ' clics, costo ' + cost(bestTerm['metrics.costMicros']) + ' y ' + n(bestTerm['metrics.conversions']) + ' conversiones.' : 'No hay términos con clics en la consulta.', date, bestTerm ? nameOf(bestTerm, ['campaign.name']) : campaign, bestTerm ? 'Fue el término con más clics devuelto por Google Ads.' : 'No se inventan palabras ni volúmenes.', bestTerm && n(bestTerm['metrics.conversions']) > 0 ? 'Alta' : 'Media', 'Intención, concordancia y página de destino.') });
  out.push({ title: 'Revisar términos costosos sin conversiones', action: costly ? 'Revisar antes de pausar o convertir en negativa.' : 'No hay alerta prioritaria en los datos recibidos.', kind: costly ? 'REVISAR' : 'SIN ALERTA', data: evidence(costly ? '«' + nameOf(costly, ['search_term_view.search_term']) + '»: ' + n(costly['metrics.clicks']) + ' clics, costo ' + cost(costly['metrics.costMicros']) + ' y 0 conversiones.' : 'No hay filas con gasto, clics y cero conversiones simultáneamente.', date, costly ? nameOf(costly, ['campaign.name']) : campaign, costly ? 'Tiene gasto sin conversiones reportadas.' : 'No se fabrica una alerta.', costly ? 'Media' : 'Baja', 'Que el seguimiento de conversiones esté funcionando.') });
  out.push({ title: 'Priorizar dispositivo por costo por conversión', action: convertingDevices.length ? 'Comparar manualmente el dispositivo de menor costo por conversión.' : 'Esperar conversiones por dispositivo.', kind: convertingDevices.length ? 'CONVERSIONES REALES' : 'DATOS INSUFICIENTES', data: evidence(convertingDevices.length ? 'Dispositivo ' + nameOf(convertingDevices[0], ['segments.device']) + ': ' + n(convertingDevices[0]['metrics.conversions']) + ' conversiones.' : 'No se reportaron conversiones por dispositivo.', date, campaign, convertingDevices.length ? 'Solo se calcula con conversiones reportadas.' : 'Clics no permiten afirmar qué dispositivo convierte mejor.', convertingDevices.length ? 'Alta' : 'Baja', 'Que la conversión sea válida y no esté duplicada.') });
  return out;
}

function writeFirestore(payload) {
  var fields = { source: { stringValue: payload.source }, accountId: { stringValue: payload.accountId }, period: { stringValue: payload.period }, updatedAt: { timestampValue: payload.updatedAt }, suggestions: { arrayValue: { values: payload.suggestions.map(function (s) { return { mapValue: { fields: { title: { stringValue: s.title }, action: { stringValue: s.action }, kind: { stringValue: s.kind }, data: { mapValue: { fields: { evidence: { stringValue: s.data.evidence }, date: { stringValue: s.data.date }, campaign: { stringValue: s.data.campaign }, reason: { stringValue: s.data.reason }, confidence: { stringValue: s.data.confidence }, confirm: { stringValue: s.data.confirm } } } } } } } }; }) } } };
  var url = 'https://firestore.googleapis.com/v1/projects/' + FIRESTORE_PROJECT_ID + '/databases/(default)/documents/' + FIRESTORE_DOCUMENT;
  UrlFetchApp.fetch(url, { method: 'patch', contentType: 'application/json', headers: { Authorization: 'Bearer ' + ScriptApp.getOAuthToken() }, payload: JSON.stringify({ fields: fields }), muteHttpExceptions: false });
}
