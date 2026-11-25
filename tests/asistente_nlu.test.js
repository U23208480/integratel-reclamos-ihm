// Pruebas del NLU del asistente. Ejecutar con: node tests/asistente_nlu.test.js
const assert = require('assert');
const { interpretar, clasificarTipo } = require('../assets/js/asistente.js');
const casos = [
  ['Registrar un reclamo: me cobraron el recibo doble este mes', 'registrar'],
  ['quiero poner un reclamo porque mi internet esta muy lento', 'registrar'],
  ['estado de mi último reclamo', 'estado'],
  ['estado del reclamo REC-2026-00015', 'estado'],
  ['¿Cuántos reclamos tengo?', 'resumen'],
  ['abrir notificaciones', 'ir'],
  ['llévame a accesibilidad', 'ir'],
  ['sí', 'si'], ['no', 'no'], ['ayuda', 'ayuda'], ['cerrar sesión', 'salir'], ['hola', 'desconocido'],
];
for (const [frase, esperado] of casos) assert.strictEqual(interpretar(frase).intent, esperado, frase);
assert.strictEqual(interpretar('estado de rec 2026 00015').codigo, 'REC-2026-00015');
const tipos = [
  ['Me cobraron el recibo doble', 'Facturación y cobros'],
  ['Mi internet esta muy lento y se corta', 'Velocidad / calidad de conexión'],
  ['No tengo servicio desde ayer, se cayo la senal', 'Avería / corte de servicio'],
  ['El tecnico nunca vino a instalar el router', 'Instalación o mantenimiento'],
  ['Maltrataron a mi familiar en la agencia', 'Atención al cliente'],
  ['Quiero hablar de otra cosa distinta aqui', 'Otro'],
];
for (const [t, esperado] of tipos) assert.strictEqual(clasificarTipo(t).tipo, esperado, t);
console.log('OK: ' + (casos.length + 1) + ' frases y ' + tipos.length + ' clasificaciones');
