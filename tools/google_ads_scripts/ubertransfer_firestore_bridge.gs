/**
 * UberTransfer · puente Apps Script -> Firestore
 *
 * Este archivo se publica como Web App independiente del script de Google Ads.
 * Ejecutar como el propietario y permitir acceso a cualquier usuario.
 *
 * Configuración obligatoria en Propiedades del proyecto:
 *   BRIDGE_TOKEN = token aleatorio de al menos 32 caracteres
 *   FIRESTORE_PROJECT_ID = ubertransfer-ops
 *
 * El token se recibe dentro del JSON porque Apps Script Web Apps no entrega
 * cabeceras HTTP a doPost(). Nunca se registra ni se devuelve.
 */
var BRIDGE = {
  DOCUMENT: 'panel/aiSuggestions',
  MAX_BODY: 250000,
  MAX_SUGGESTIONS: 30,
  WINDOW_MS: 10 * 60 * 1000
};

// Ejecutar una vez desde el editor para solicitar los permisos del puente.
// No imprime ni guarda el token OAuth.
function autorizarPuente() {
  var token = ScriptApp.getOAuthToken();
  if (!token) throw new Error('No se pudo obtener el token OAuth del proyecto.');
  console.log('Permisos del puente autorizados.');
}

function doGet() {
  return json_({ ok: true, service: 'ubertransfer-firestore-bridge' });
}

function doPost(e) {
  try {
    var body = parseBody_(e);
    if (!tokenValido_(body.token)) return json_({ ok: false, error: 'No autorizado' });
    if (typeof body.id !== 'string' || !/^[A-Za-z0-9][A-Za-z0-9_-]{7,63}$/.test(body.id)) {
      return json_({ ok: false, error: 'id invalido' });
    }
    if (typeof body.ts !== 'number' || Math.abs(Date.now() - body.ts) > BRIDGE.WINDOW_MS) {
      return json_({ ok: false, error: 'timestamp fuera de ventana' });
    }
    validarPayload_(body.payload);
    escribirFirestore_(body.payload);
    return json_({ ok: true, id: body.id });
  } catch (error) {
    console.error('Bridge error: ' + error.message);
    return json_({ ok: false, error: 'No fue posible guardar las sugerencias' });
  }
}

function parseBody_(e) {
  if (!e || !e.postData || typeof e.postData.contents !== 'string') throw new Error('Solicitud vacia');
  if (e.postData.contents.length > BRIDGE.MAX_BODY) throw new Error('Solicitud demasiado grande');
  var body = JSON.parse(e.postData.contents);
  if (!body || typeof body !== 'object') throw new Error('JSON invalido');
  return body;
}

function tokenValido_(candidate) {
  var expected = PropertiesService.getScriptProperties().getProperty('BRIDGE_TOKEN') || '';
  if (!expected || typeof candidate !== 'string' || candidate.length !== expected.length) return false;
  var difference = 0;
  for (var i = 0; i < expected.length; i++) difference |= expected.charCodeAt(i) ^ candidate.charCodeAt(i);
  return difference === 0;
}

function validarPayload_(payload) {
  if (!payload || typeof payload !== 'object') throw new Error('payload invalido');
  if (typeof payload.source !== 'string' || typeof payload.accountId !== 'string' || typeof payload.period !== 'string') {
    throw new Error('payload sin metadatos obligatorios');
  }
  if (!Array.isArray(payload.suggestions) || payload.suggestions.length > BRIDGE.MAX_SUGGESTIONS) {
    throw new Error('cantidad de sugerencias invalida');
  }
  if (JSON.stringify(payload).length > BRIDGE.MAX_BODY) throw new Error('payload demasiado grande');
}

function escribirFirestore_(payload) {
  var projectId = PropertiesService.getScriptProperties().getProperty('FIRESTORE_PROJECT_ID');
  if (!projectId) throw new Error('FIRESTORE_PROJECT_ID no configurado');
  var fields = {
    source: firestoreValue_(payload.source),
    accountId: firestoreValue_(payload.accountId),
    period: firestoreValue_(payload.period),
    updatedAt: { timestampValue: String(payload.updatedAt || new Date().toISOString()) },
    suggestions: firestoreValue_(payload.suggestions),
    queryStatus: firestoreValue_(payload.queryStatus || {}),
    queryErrors: firestoreValue_(payload.queryErrors || [])
  };
  var url = 'https://firestore.googleapis.com/v1/projects/' + encodeURIComponent(projectId) + '/databases/(default)/documents/' + BRIDGE.DOCUMENT;
  var response = UrlFetchApp.fetch(url, {
    method: 'patch',
    contentType: 'application/json',
    headers: { Authorization: 'Bearer ' + ScriptApp.getOAuthToken() },
    payload: JSON.stringify({ fields: fields }),
    muteHttpExceptions: true
  });
  if (response.getResponseCode() < 200 || response.getResponseCode() >= 300) {
    throw new Error('Firestore HTTP ' + response.getResponseCode());
  }
}

function firestoreValue_(value) {
  if (value === null || value === undefined) return { nullValue: null };
  if (typeof value === 'string') return { stringValue: value };
  if (typeof value === 'boolean') return { booleanValue: value };
  if (typeof value === 'number') return { doubleValue: value };
  if (Array.isArray(value)) return { arrayValue: { values: value.map(firestoreValue_) } };
  var fields = {};
  Object.keys(value).forEach(function (key) { fields[key] = firestoreValue_(value[key]); });
  return { mapValue: { fields: fields } };
}

function json_(value) {
  return ContentService.createTextOutput(JSON.stringify(value)).setMimeType(ContentService.MimeType.JSON);
}
