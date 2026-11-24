# -*- coding: utf-8 -*-
"""Banco de pruebas: corre app.py contra SQLite en lugar de MySQL.
No forma parte del sistema; sirve para verificar la API sin levantar MySQL."""
import os, re, sys, sqlite3, json, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("SMTP_HOST", "")          # correo en modo simulado

DB_FILE = os.path.join(tempfile.gettempdir(), "harness_integratel.sqlite")
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)


def _mysql_a_sqlite(sql):
    sql = re.sub(r"\s*ENGINE=InnoDB DEFAULT CHARSET=utf8mb4", "", sql, flags=re.I)
    sql = re.sub(r"INT AUTO_INCREMENT PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT", sql, flags=re.I)
    sql = re.sub(r"TINYINT\(1\)", "INTEGER", sql, flags=re.I)
    sql = re.sub(r",\s*INDEX \w+ \([^)]*\)", "", sql, flags=re.I)
    return sql


class SQLiteConn:
    def __init__(self, database=None):
        self.conn = sqlite3.connect(DB_FILE)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys=ON")

    def execute(self, query, params=()):
        q = _mysql_a_sqlite(query)
        if q.strip().upper().startswith("SHOW COLUMNS FROM"):
            tabla = q.strip().split()[-1]
            cur = self.conn.execute(f"PRAGMA table_info({tabla})")
            filas = [{"Field": r["name"]} for r in cur.fetchall()]
            return _Fake(filas)
        cur = self.conn.execute(q, params)
        return _Cur(cur)

    def executescript(self, script):
        self.conn.executescript(_mysql_a_sqlite(script))

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()


class _Cur:
    def __init__(self, cur): self.cur = cur
    def fetchone(self):
        r = self.cur.fetchone()
        return dict(r) if r else None
    def fetchall(self):
        return [dict(r) for r in self.cur.fetchall()]


class _Fake:
    def __init__(self, filas): self.filas = filas
    def fetchone(self): return self.filas[0] if self.filas else None
    def fetchall(self): return self.filas


import app as APP
APP.MySQLConn = SQLiteConn
APP.init_db()
APP.app.config["TESTING"] = True
cliente = APP.app.test_client()
