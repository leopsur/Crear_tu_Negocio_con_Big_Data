"""
03_exportar_json.py - Genera un archivo .json distinto por cada base de datos de ActivityLeo.

No se vuelcan tablas enteras: cada consulta UNE varias tablas (JOIN) y devuelve solo
los datos más útiles para tomar decisiones. En cada JSON se explica por qué importan.

  MySQL      -> json/mysql_alumnos.json       (qué interesa y qué se vota entre los alumnos)
  PostgreSQL -> json/postgres_comunidad.json  (vecinos y tendencias en redes)
  MariaDB    -> json/mariadb_actividades.json (actividades finales, aforo y apoyo recibido)

Uso:  python 03_exportar_json.py
(Ejecutar antes 01_crear_bases_datos.py y 02_rellenar_faker.py)
"""
import json
import os
from datetime import date, datetime
from decimal import Decimal

from config import BASES_DE_DATOS, conectar

CARPETA_JSON = os.path.join(os.path.dirname(__file__), "..", "json")

# Consultas por base de datos

CONSULTAS = {
    "mysql": {
        "archivo": "mysql_alumnos.json",
        "consultas": [
            {
                "nombre": "ranking_categorias_por_interes_de_alumnos",
                "por_que_es_importante": (
                    "Cruza Alumnos, Preferencias_Alumnos y Categorias_Interes. Dice qué temas "
                    "gustan más a los alumnos y cuántos alumnos los eligen, así el instituto "
                    "sabe en qué talleres invertir."
                ),
                "sql": """
                    SELECT c.nombre_categoria,
                           COUNT(DISTINCT a.id_alumno) AS alumnos_interesados,
                           ROUND(AVG(pa.nivel_interes), 2) AS interes_medio
                    FROM Preferencias_Alumnos pa
                    JOIN Alumnos a ON a.id_alumno = pa.id_alumno
                    JOIN Categorias_Interes c ON c.id_categoria = pa.id_categoria
                    GROUP BY c.nombre_categoria
                    ORDER BY interes_medio DESC, alumnos_interesados DESC
                """,
            },
            {
                "nombre": "propuestas_mas_votadas_por_alumnos_y_vecinos",
                "por_que_es_importante": (
                    "Cruza Propuestas_actividades, Categorias_Interes y Votaciones. Muestra qué "
                    "propuestas tienen más apoyo y cuántos votos vienen de alumnos y de vecinos, "
                    "para elegir las actividades que de verdad quiere la comunidad."
                ),
                "sql": """
                    SELECT p.titulo_propuesta,
                           c.nombre_categoria,
                           COUNT(v.id_voto) AS votos_totales,
                           SUM(CASE WHEN v.id_alumno IS NOT NULL THEN 1 ELSE 0 END) AS votos_alumnos,
                           SUM(CASE WHEN v.id_vecino IS NOT NULL THEN 1 ELSE 0 END) AS votos_vecinos
                    FROM Propuestas_actividades p
                    JOIN Categorias_Interes c ON c.id_categoria = p.id_categoria
                    JOIN Votaciones v ON v.id_propuesta = p.id_propuesta
                    GROUP BY p.id_propuesta, p.titulo_propuesta, c.nombre_categoria
                    ORDER BY votos_totales DESC
                    LIMIT 10
                """,
            },
        ],
    },
    "postgres": {
        "archivo": "postgres_comunidad.json",
        "consultas": [
            {
                "nombre": "interes_de_vecinos_por_categoria_y_frecuencia",
                "por_que_es_importante": (
                    "Cruza Vecinos, Preferencias_Vecinos y Categorias_Interes. Indica qué "
                    "actividades quieren los vecinos y con qué frecuencia, para planificar "
                    "talleres abiertos al barrio con un calendario realista."
                ),
                "sql": """
                    SELECT c.nombre_categoria,
                           pv.frecuencia_deseada,
                           COUNT(DISTINCT v.id_vecino) AS vecinos_interesados
                    FROM Preferencias_Vecinos pv
                    JOIN Vecinos v ON v.id_vecino = pv.id_vecino
                    JOIN Categorias_Interes c ON c.id_categoria = pv.id_categoria
                    GROUP BY c.nombre_categoria, pv.frecuencia_deseada
                    ORDER BY vecinos_interesados DESC
                    LIMIT 15
                """,
            },
            {
                "nombre": "tendencias_en_redes_por_categoria",
                "por_que_es_importante": (
                    "Cruza Tendencias_Redes y Categorias_Interes. Detecta qué temas están de "
                    "moda en las redes y cuáles son sus palabras clave más buscadas, para "
                    "anticiparse a lo que pedirán alumnos y vecinos."
                ),
                "sql": """
                    SELECT c.nombre_categoria,
                           SUM(t.volumen_busquedas) AS busquedas_totales,
                           MAX(t.volumen_busquedas) AS maximo_una_palabra,
                           COUNT(t.id_tendencia) AS palabras_clave
                    FROM Tendencias_Redes t
                    JOIN Categorias_Interes c ON c.id_categoria = t.id_categoria
                    GROUP BY c.nombre_categoria
                    ORDER BY busquedas_totales DESC
                """,
            },
        ],
    },
    "mariadb": {
        "archivo": "mariadb_actividades.json",
        "consultas": [
            {
                "nombre": "actividades_finales_con_espacio_y_apoyo",
                "por_que_es_importante": (
                    "Cruza Actividades_finales, Propuestas_actividades, Espacios_disponibles y "
                    "Votaciones. Comprueba si el espacio elegido tiene aforo suficiente para el "
                    "apoyo que recibió cada actividad, y evita elegir salas demasiado pequeñas."
                ),
                "sql": """
                    SELECT af.id_actividad,
                           p.titulo_propuesta,
                           e.nombre_espacio,
                           e.capacidad_maxima,
                           af.horario_fijo,
                           COUNT(v.id_voto) AS votos_recibidos
                    FROM Actividades_finales af
                    JOIN Propuestas_actividades p ON p.id_propuesta = af.id_propuesta
                    JOIN Espacios_disponibles e ON e.id_espacio = af.id_espacio
                    LEFT JOIN Votaciones v ON v.id_propuesta = p.id_propuesta
                    GROUP BY af.id_actividad, p.titulo_propuesta, e.nombre_espacio,
                             e.capacidad_maxima, af.horario_fijo
                    ORDER BY votos_recibidos DESC
                """,
            },
            {
                "nombre": "interes_de_alumnos_frente_a_tendencias_en_redes",
                "por_que_es_importante": (
                    "Cruza Categorias_Interes, Preferencias_Alumnos y Tendencias_Redes. Compara lo "
                    "que piden los alumnos con lo que está de moda fuera del instituto y detecta "
                    "temas con mucha demanda en redes y poca oferta interna."
                ),
                "sql": """
                    SELECT c.nombre_categoria,
                           (SELECT ROUND(AVG(pa.nivel_interes), 2)
                              FROM Preferencias_Alumnos pa
                             WHERE pa.id_categoria = c.id_categoria) AS interes_medio_alumnos,
                           (SELECT COALESCE(SUM(t.volumen_busquedas), 0)
                              FROM Tendencias_Redes t
                             WHERE t.id_categoria = c.id_categoria) AS busquedas_en_redes
                    FROM Categorias_Interes c
                    ORDER BY busquedas_en_redes DESC
                """,
            },
        ],
    },
}


def a_json(valor):
    """Convierte fechas y decimales para poder guardarlos en JSON."""
    if isinstance(valor, Decimal):
        return float(valor)
    if isinstance(valor, (datetime, date)):
        return valor.isoformat()
    return str(valor)


def ejecutar(cursor, tipo, sql):
    cursor.execute(sql)
    filas = cursor.fetchall()
    if tipo == "postgres":  # psycopg2 devuelve tuplas: las convertimos a diccionarios
        columnas = [col[0] for col in cursor.description]
        filas = [dict(zip(columnas, fila)) for fila in filas]
    return list(filas)


def exportar(nombre_bd):
    cfg = BASES_DE_DATOS[nombre_bd]
    definicion = CONSULTAS[nombre_bd]
    print(f"\n== {nombre_bd} ==")
    conexion = conectar(nombre_bd)
    cursor = conexion.cursor()

    resultado = {"proyecto": "ActivityLeo", "base_datos": nombre_bd, "consultas": []}
    for consulta in definicion["consultas"]:
        filas = ejecutar(cursor, cfg["tipo"], consulta["sql"])
        resultado["consultas"].append({
            "nombre": consulta["nombre"],
            "por_que_es_importante": consulta["por_que_es_importante"],
            "sql": " ".join(consulta["sql"].split()),
            "total_filas": len(filas),
            "resultados": filas,
        })
        print(f"  {consulta['nombre']}: {len(filas)} filas")
    conexion.close()

    os.makedirs(CARPETA_JSON, exist_ok=True)
    ruta = os.path.join(CARPETA_JSON, definicion["archivo"])
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(resultado, archivo, ensure_ascii=False, indent=2, default=a_json)
    print(f"  guardado en {os.path.normpath(ruta)}")


if __name__ == "__main__":
    for bd in BASES_DE_DATOS:
        exportar(bd)
    print("\nListo: un .json distinto por cada base de datos.")
