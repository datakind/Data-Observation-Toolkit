FROM python:3.8-slim-buster

WORKDIR app/
# Switch to the root user to install system-level dependencies if needed
USER root

RUN sed -i 's|deb.debian.org|archive.debian.org|g' /etc/apt/sources.list \
 && sed -i 's|security.debian.org|archive.debian.org|g' /etc/apt/sources.list \
 && sed -i '/buster-updates/d' /etc/apt/sources.list \
 && printf 'Acquire::Check-Valid-Until "false";\n' > /etc/apt/apt.conf.d/99no-check-valid-until \
 && rm -f /etc/apt/sources.list.d/pgdg.list \
 && rm -f /etc/apt/sources.list.d/mssql-release.list \
 && apt-get update

RUN pip install --upgrade pip

# This uses the requirements as defined in the dot directory
COPY ./dot/requirements_dot.txt requirements_dot.txt
COPY ./dot/install_dot.sh install_dot.sh
RUN ./install_dot.sh

# This will be overwritten if using local mounts, but keeping here for the demo build
COPY ../ /app
COPY ./docker/dot/dot_config.yml /app/dot/config/dot_config.yml
COPY ./dot/config/example/self_tests/dot_config_docker.yml /app/dot/self_tests/data/base_self_test/dot_config.yml

# Install psql, useful
RUN apt-get -y install postgresql-client

#CMD [ "python3" ]
CMD tail -f /dev/null
