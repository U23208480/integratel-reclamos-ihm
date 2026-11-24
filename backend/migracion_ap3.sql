-- ============================================================
-- INTEGRATEL PERÚ — Migración AP3
-- Accesibilidad, idiomas, verificación de correo y baja de cuenta
--
-- No hace falta ejecutarlo a mano: al arrancar `python backend/app.py`
-- se crean las tablas y se agregan las columnas que falten, sin tocar
-- los datos ya cargados. Este archivo sirve para revisar la migración
-- en MySQL Workbench y para documentarla en el informe.
-- ============================================================

USE integratel_reclamos;

-- ------------------------------------------------------------
-- 1 · usuarios: doce columnas nuevas
-- ------------------------------------------------------------
-- preferencias            Los 23 ajustes de accesibilidad, en JSON
-- idioma                  es | en | qu (quechua) | ay (aymara)
-- estado_cuenta           activa | desactivada | eliminada
-- correo_verificado       0 hasta que la persona abre el enlace del correo 1
-- codigo_verificacion     Código del correo 1, vence en 24 horas
-- codigo_baja             Código de 6 dígitos del correo 4, vence en 10 minutos
-- baja_solicitada_at      Cuándo pidió eliminar la cuenta
-- baja_efectiva_at        Fin del periodo de gracia (30 días)
-- notificaciones_silenciadas  Alternativa intermedia a eliminar la cuenta
-- ultimo_acceso           Para el aviso de sesión por inactividad

ALTER TABLE usuarios
  ADD COLUMN preferencias               TEXT                  NULL,
  ADD COLUMN idioma                     VARCHAR(5)   NOT NULL DEFAULT 'es',
  ADD COLUMN estado_cuenta              VARCHAR(20)  NOT NULL DEFAULT 'activa',
  ADD COLUMN correo_verificado          TINYINT(1)   NOT NULL DEFAULT 0,
  ADD COLUMN codigo_verificacion        VARCHAR(12)           NULL,
  ADD COLUMN codigo_expira              VARCHAR(40)           NULL,
  ADD COLUMN codigo_baja                VARCHAR(12)           NULL,
  ADD COLUMN codigo_baja_expira         VARCHAR(40)           NULL,
  ADD COLUMN baja_solicitada_at         VARCHAR(40)           NULL,
  ADD COLUMN baja_efectiva_at           VARCHAR(40)           NULL,
  ADD COLUMN notificaciones_silenciadas TINYINT(1)   NOT NULL DEFAULT 0,
  ADD COLUMN ultimo_acceso              VARCHAR(40)           NULL;

-- Las cuentas que ya existían quedan activas y con el correo dado por verificado,
-- para que la migración no deje a nadie fuera del portal.
UPDATE usuarios
   SET estado_cuenta    = 'activa',
       correo_verificado = 1
 WHERE estado_cuenta IS NULL OR estado_cuenta = '';

-- ------------------------------------------------------------
-- 2 · notificaciones: una fila por cada aviso que ve la persona
--     (alimenta el estado 3 del catálogo: vacío por historial)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS notificaciones (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    dni        VARCHAR(12)  NOT NULL,
    tipo       VARCHAR(40)  NOT NULL,     -- reclamo | cuenta | seguridad
    titulo     VARCHAR(200) NOT NULL,
    detalle    TEXT,
    reclamo_id VARCHAR(20),
    leida      TINYINT(1)   NOT NULL DEFAULT 0,
    created_at VARCHAR(40)  NOT NULL,
    INDEX idx_notif_dni (dni)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- 3 · bajas_cuenta: registro de cada baja, con su periodo de gracia
--     Queda aunque la cuenta se restaure, para poder auditar el flujo.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS bajas_cuenta (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    dni           VARCHAR(12)  NOT NULL,
    motivo        VARCHAR(120),
    comentario    TEXT,
    solicitada_at VARCHAR(40)  NOT NULL,
    efectiva_at   VARCHAR(40)  NOT NULL,  -- solicitada_at + 30 días
    restaurada_at VARCHAR(40),            -- se llena si la persona se arrepiente
    INDEX idx_baja_dni (dni)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- 4 · Comprobaciones
-- ------------------------------------------------------------
-- SHOW COLUMNS FROM usuarios;
-- SELECT dni, nombre, idioma, estado_cuenta, correo_verificado FROM usuarios;
-- SELECT JSON_EXTRACT(preferencias, '$.tema')      AS tema,
--        JSON_EXTRACT(preferencias, '$.contraste') AS contraste,
--        JSON_EXTRACT(preferencias, '$.fs')        AS tamano_texto
--   FROM usuarios WHERE dni = '71234567';
-- SELECT * FROM notificaciones ORDER BY created_at DESC LIMIT 10;
-- SELECT * FROM bajas_cuenta;
