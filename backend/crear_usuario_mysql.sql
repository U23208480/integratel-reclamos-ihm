-- ============================================================
-- INTEGRATEL PERU — Crea la base de datos y un usuario dedicado
-- para que el backend Flask se conecte por si solo, sin usar tu
-- cuenta root personal.
--
-- COMO USARLO:
-- 1. Abre MySQL Workbench y conecta con tu conexion habitual (root).
-- 2. Abre este archivo (File > Open SQL Script...) o pega su
--    contenido en una pestaña nueva.
-- 3. Ejecuta TODO el script (icono del rayo, o Ctrl+Shift+Enter).
-- ============================================================

CREATE DATABASE IF NOT EXISTS integratel_reclamos
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'integratel_app'@'localhost' IDENTIFIED BY 'IntegratelReclamos2026!';

GRANT ALL PRIVILEGES ON integratel_reclamos.* TO 'integratel_app'@'localhost';

FLUSH PRIVILEGES;

-- Verificacion rapida (deberia devolver 1 fila con el nuevo usuario)
SELECT User, Host FROM mysql.user WHERE User = 'integratel_app';
