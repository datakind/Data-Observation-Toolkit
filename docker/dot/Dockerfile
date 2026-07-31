# Start with the exact same Airflow image you are already using
FROM apache/airflow:2.2.4-python3.8

# Switch to the root user to install system-level dependencies if needed
USER root

RUN sed -i 's|deb.debian.org|archive.debian.org|g' /etc/apt/sources.list \
 && sed -i 's|security.debian.org|archive.debian.org|g' /etc/apt/sources.list \
 && sed -i '/buster-updates/d' /etc/apt/sources.list \
 && printf 'Acquire::Check-Valid-Until "false";\n' > /etc/apt/apt.conf.d/99no-check-valid-until \
 && rm -f /etc/apt/sources.list.d/pgdg.list \
 && rm -f /etc/apt/sources.list.d/mssql-release.list \
 && apt-get update

RUN apt-get -y install postgresql-client


# Switch back to the 'airflow' user (best practice for Airflow images)
USER airflow

# Copy your DOT requirements and install script
COPY --chown=airflow:root ./dot/requirements_dot.txt /tmp/requirements_dot.txt
COPY --chown=airflow:root ./dot/install_dot.sh /tmp/install_dot.sh

# Run your install script
RUN chmod +x /tmp/install_dot.sh && cd /tmp && ./install_dot.sh
