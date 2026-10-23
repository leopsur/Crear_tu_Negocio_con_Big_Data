"""
config.py - Conexiones a las 3 bases de datos de ActivityLeo.

Los datos coinciden con los Dockerfile y el docker-compose.yml:
  - MySQL      -> localhost:3307
  - PostgreSQL -> localhost:5433
  - MariaDB    -> localhost:3308
"""
import time

import pymysql
import psycopg2

USUARIO = "leo"
PASSWORD = "leo1234"
NOMBRE_BD = "activityleo"

BASES_DE_DATOS = {
    "mysql":    {"tipo": "mysql",    "host": "localhost", "puerto": 3307},
    "postgres": {"tipo": "postgres", "host": "localhost", "puerto": 5433},
    "mariadb":  {"tipo": "mysql",    "host": "localhost", "puerto": 3308},
}


def conectar(nombre, reintentos=30):
    """Devuelve una conexión abierta. Espera a que el contenedor termine de arrancar."""
    cfg = BASES_DE_DATOS[nombre]
    ultimo_error = None
    for _ in range(reintentos):
        try:
            if cfg["tipo"] == "mysql":
                return pymysql.connect(
                    host=cfg["host"], port=cfg["puerto"], user=USUARIO,
                    password=PASSWORD, database=NOMBRE_BD, charset="utf8mb4",
                    cursorclass=pymysql.cursors.DictCursor,
                )
            return psycopg2.connect(
                host=cfg["host"], port=cfg["puerto"], user=USUARIO,
                password=PASSWORD, dbname=NOMBRE_BD,
            )
        except Exception as error:  # el contenedor aún está arrancando
            ultimo_error = error
            print(f"  esperando a {nombre}... ({error.__class__.__name__})")
            time.sleep(3)
    raise RuntimeError(f"No se pudo conectar con {nombre}: {ultimo_error}")
