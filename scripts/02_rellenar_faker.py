"""
02_rellenar_faker.py - Rellena las 3 bases de datos de ActivityLeo con datos falsos
generados con Faker (idioma español de España).

Comandos (providers) de Faker usados, 11 distintos:
  1.  fake.name()                 -> provider person    : nombre de alumnos y vecinos
  2.  fake.date_of_birth()        -> provider date_time : fecha de nacimiento de los alumnos
  3.  fake.email()                -> provider internet  : correo institucional
  4.  fake.postcode()             -> provider address   : código postal de los vecinos
  5.  fake.word()                 -> provider lorem     : nombre de los espacios
  6.  fake.sentence()             -> provider lorem     : descripción de las categorías
  7.  fake.catch_phrase()         -> provider company   : lema de cada propuesta de actividad
  8.  fake.random_int()           -> provider python    : niveles de interés, capacidad, volumen
  9.  fake.random_element()       -> provider misc/base : curso, rango de edad, origen, frecuencia
  10. fake.date_time_between()    -> provider date_time : horario fijo de las actividades finales
  11. fake.hashtag()              -> provider internet  : palabra clave de las tendencias en redes

Uso:  python 02_rellenar_faker.py
(Ejecutar antes 01_crear_bases_datos.py)
"""
import random

from faker import Faker

from config import BASES_DE_DATOS, conectar

TABLAS = [
    ("Alumnos", "id_alumno"), ("Vecinos", "id_vecino"),
    ("Categorias_Interes", "id_categoria"), ("Espacios_disponibles", "id_espacio"),
    ("Preferencias_Alumnos", "id_preferencia"), ("Preferencias_Vecinos", "id_preferencia_vec"),
    ("Tendencias_Redes", "id_tendencia"), ("Propuestas_actividades", "id_propuesta"),
    ("Votaciones", "id_voto"), ("Actividades_finales", "id_actividad"),
]

CATEGORIAS = [
    "Música", "Videojuegos", "Deportes", "Arte y dibujo", "Tecnología", "Cocina",
    "Teatro", "Cine", "Idiomas", "Ajedrez", "Fotografía", "Podcasts",
]
CURSOS = ["1º ESO", "2º ESO", "3º ESO", "4º ESO", "1º Bachillerato", "2º Bachillerato"]
RANGOS_EDAD = ["18-25", "26-35", "36-50", "51-65", "65+"]
FRECUENCIAS = ["Semanal", "Quincenal", "Mensual"]
ORIGENES = ["Alumnos", "Vecinos", "Redes"]
TIPOS_ACTIVIDAD = ["Taller", "Torneo", "Club", "Charla", "Concierto"]
TIPOS_ESPACIO = ["Aula", "Sala", "Patio", "Salón"]


def generar_datos(semilla):
    """Genera todas las filas en memoria. Cada base de datos usa una semilla distinta."""
    fake = Faker("es_ES")
    Faker.seed(semilla)
    random.seed(semilla)

    alumnos = []
    for i in range(1, 301):
        alumnos.append((
            i,
            fake.name(),                                                    # person
            fake.random_element(CURSOS),                                    # random_element
            fake.date_of_birth(minimum_age=12, maximum_age=18),             # date_of_birth
            f"{i}.{fake.email()}",                                          # internet (único)
        ))

    vecinos = [
        (i, fake.name(), fake.postcode(), fake.random_element(RANGOS_EDAD))  # person, address
        for i in range(1, 201)
    ]

    categorias = [
        (i, nombre, fake.sentence(nb_words=8))                              # lorem
        for i, nombre in enumerate(CATEGORIAS, start=1)
    ]
    ids_categoria = [c[0] for c in categorias]

    espacios = [
        (i, f"{fake.random_element(TIPOS_ESPACIO)} {fake.word()} {i}",     # lorem
         fake.random_int(min=15, max=200))                                  # python
        for i in range(1, 9)
    ]

    pref_alumnos, id_pref = [], 1
    for alumno in alumnos:
        for cat in random.sample(ids_categoria, fake.random_int(min=2, max=4)):
            pref_alumnos.append((id_pref, alumno[0], cat, fake.random_int(min=1, max=5)))
            id_pref += 1

    pref_vecinos, id_pref = [], 1
    for vecino in vecinos:
        for cat in random.sample(ids_categoria, fake.random_int(min=1, max=3)):
            pref_vecinos.append((id_pref, vecino[0], cat, fake.random_element(FRECUENCIAS)))
            id_pref += 1

    tendencias = [
        (i, random.choice(ids_categoria), fake.word(),                   # internet
         fake.random_int(min=100, max=50000))
        for i in range(1, 151)
    ]

    propuestas = []
    for i in range(1, 41):
        cat = random.choice(categorias)
        titulo = f"{fake.random_element(TIPOS_ACTIVIDAD)} de {cat[1]} - {fake.catch_phrase()}"  # company
        propuestas.append((i, cat[0], titulo[:200], fake.random_element(ORIGENES)))

    votaciones, vistos, id_voto = [], set(), 1
    while len(votaciones) < 1200:
        propuesta = random.choice(propuestas)[0]
        if random.random() < 0.7:
            persona = ("a", random.choice(alumnos)[0])
        else:
            persona = ("v", random.choice(vecinos)[0])
        if (propuesta, persona) in vistos:
            continue
        vistos.add((propuesta, persona))
        id_alumno = persona[1] if persona[0] == "a" else None
        id_vecino = persona[1] if persona[0] == "v" else None
        votaciones.append((id_voto, propuesta, id_alumno, id_vecino))
        id_voto += 1

    actividades = []
    for i, propuesta in enumerate(random.sample(propuestas, 15), start=1):
        actividades.append((
            i, propuesta[0], random.choice(espacios)[0],
            fake.date_time_between(start_date="+7d", end_date="+120d"),     # date_time
        ))

    return {
        "Alumnos": alumnos, "Vecinos": vecinos, "Categorias_Interes": categorias,
        "Espacios_disponibles": espacios, "Preferencias_Alumnos": pref_alumnos,
        "Preferencias_Vecinos": pref_vecinos, "Tendencias_Redes": tendencias,
        "Propuestas_actividades": propuestas, "Votaciones": votaciones,
        "Actividades_finales": actividades,
    }


def insertar(nombre_bd, datos):
    cfg = BASES_DE_DATOS[nombre_bd]
    print(f"\n== {nombre_bd} ==")
    conexion = conectar(nombre_bd)
    cursor = conexion.cursor()

    if cfg["tipo"] == "mysql":
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        for tabla, _ in reversed(TABLAS):
            cursor.execute(f"TRUNCATE TABLE {tabla}")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    else:
        nombres = ", ".join(t for t, _ in TABLAS)
        cursor.execute(f"TRUNCATE TABLE {nombres} RESTART IDENTITY CASCADE")

    for tabla, _ in TABLAS:  # orden correcto: primero las tablas padre
        filas = datos[tabla]
        marcas = ", ".join(["%s"] * len(filas[0]))
        cursor.executemany(f"INSERT INTO {tabla} VALUES ({marcas})", filas)
        print(f"  {tabla}: {len(filas)} filas")

    if cfg["tipo"] == "postgres":
        # Como hemos insertado ids a mano, ajustamos los contadores automáticos
        for tabla, clave in TABLAS:
            cursor.execute(
                f"SELECT setval(pg_get_serial_sequence('{tabla.lower()}', '{clave}'), "
                f"(SELECT MAX({clave}) FROM {tabla}))"
            )

    conexion.commit()
    conexion.close()


if __name__ == "__main__":
    for semilla, bd in enumerate(BASES_DE_DATOS, start=1):
        insertar(bd, generar_datos(semilla=semilla * 100))
    print("\nListo: las 3 bases de datos están rellenas (con datos distintos en cada una).")
