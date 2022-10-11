#!/usr/bin/env bash
airflow db init
airflow users create -r Admin -u admin -e admin@example.com -f admin -l user -p admin1234
airflow webserver