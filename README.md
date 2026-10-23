# ActivityLeo

Plataforma de Big Data que analiza de forma anónima los gustos e intereses de los alumnos y vecinos del barrio para organizar talleres y actividades que de verdad les gusten.

Este repositorio contiene la parte práctica: **3 bases de datos en Docker** (MySQL, PostgreSQL y MariaDB) con el mismo esquema de **10 tablas**, y 3 scripts de Python.

## Estructura

```
ActivityLeo/
├── docker-compose.yml
├── mysql/Dockerfile
├── postgres/Dockerfile
├── mariadb/Dockerfile
├── requirements.txt
├── Diagrama_ER_ActivityLeo.drawio   # diagrama ER del que salen las 10 tablas
├── scripts/
│   ├── config.py                  # conexiones a las 3 bases de datos
│   ├── 01_crear_bases_datos.py    # crea las 10 tablas en las 3 bases de datos
│   ├── 02_rellenar_faker.py       # rellena todo con Faker (11 providers)
│   └── 03_exportar_json.py        # consultas con JOIN -> 1 .json por base de datos
└── json/                          # se generan al ejecutar el paso 3
```

## Pasos para probarlo

1. Arrancar las 3 bases de datos (cada una con su volumen):
   ```
   docker compose up -d --build
   ```
2. Instalar las librerías de Python:
   ```
   pip install -r requirements.txt
   ```
3. Crear las tablas, rellenarlas y exportar los JSON:
   ```
   cd scripts
   python 01_crear_bases_datos.py
   python 02_rellenar_faker.py
   python 03_exportar_json.py
   ```

## Conexión desde DBeaver

| Base de datos | Host      | Puerto | Base de datos | Usuario | Contraseña |
|---------------|-----------|--------|---------------|---------|------------|
| MySQL         | localhost | 3307   | activityleo   | root     | root1234    |
| PostgreSQL    | localhost | 5433   | activityleo   | leo     | leo1234    |
| MariaDB       | localhost | 3308   | activityleo   | root     | root1234    |

Si DBeaver da el error `Public Key Retrieval is not allowed` con MySQL, hay que poner `allowPublicKeyRetrieval=true` en las propiedades del driver.

## Tablas

Alumnos, Vecinos, Categorias_Interes, Espacios_disponibles, Preferencias_Alumnos, Preferencias_Vecinos, Tendencias_Redes, Propuestas_actividades, Votaciones y Actividades_finales.

## JSON generados

Cada base de datos genera un `.json` distinto, con consultas que unen varias tablas y una explicación de por qué esos datos son importantes:

- `json/mysql_alumnos.json`: ranking de intereses de los alumnos y propuestas más votadas.
- `json/postgres_comunidad.json`: intereses de los vecinos y tendencias en redes.
- `json/mariadb_actividades.json`: actividades finales con su espacio y apoyo, e interés de alumnos frente a tendencias.
