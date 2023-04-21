--CREATE SCHEMA IF NOT EXISTS dot_config;

--CREATE TABLE dot_config.dot(
--output_schema_suffix VARCHAR(255) NOT NULL DEFAULT 'test'
--);

--INSERT INTO dot_config.dot(output_schema_suffix)
--VALUES('tests');

CREATE TABLE airflow.connection(
id INTEGER PRIMARY KEY,
conn_id VARCHAR(255),
conn_type VARCHAR(255),
description VARCHAR(255),
host VARCHAR(255),
schema VARCHAR(255),
login VARCHAR(255),
password VARCHAR(255),
port VARCHAR(255),
is_encrypted BOOLEAN,
is_extra_encrypted BOOLEAN,
extra VARCHAR(255)
);

INSERT INTO dot_config.dot_db_config(id,conn_id,conn_type,description,host,schema,login,password,port)
VALUES(1,'dot_db','postgres','dot_db','dot','postgres','','5432');
--ToDo:Hashthepasswordcolumn
