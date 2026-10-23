FROM mariadb:10.11

ENV MARIADB_ROOT_PASSWORD=root1234
ENV MARIADB_DATABASE=activityleo
ENV MARIADB_USER=leo
ENV MARIADB_PASSWORD=leo1234

EXPOSE 3306

# Volumen para que los datos no se pierdan al borrar el contenedor
VOLUME /var/lib/mysql
