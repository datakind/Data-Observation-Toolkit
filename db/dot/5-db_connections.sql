CREATE SCHEMA IF NOT EXISTS dot_config;

CREATE TABLE dot_config.dot(
output_schema_suffix VARCHAR(255) NOT NULL DEFAULT 'test'
);

INSERT INTO dot_config.dot(output_schema_suffix)
VALUES('tests');

CREATE TABLE dot_config.dot_db_config(
connection_name VARCHAR(255) PRIMARY KEY,
type VARCHAR(255),
host VARCHAR(255),
user_name VARCHAR(255),
password VARCHAR(255),
port VARCHAR(255),
dbname VARCHAR(255),
schema VARCHAR(255),
threads VARCHAR(255)
);

INSERT INTO dot_config.dot_db_config(connection_name,type,host,user_name,password,port,dbname,schema,threads)
VALUES('dot_db','postgres','dot_db','postgres','','5432','dot_db','dot','4');
INSERT INTO dot_config.dot_db_config(connection_name,type,host,user_name,password,port,dbname,schema,threads)
VALUES('ScanProject1','postgres','dot_db','postgres','','5432','dot_db','public','4');
--ToDo:Hashthepasswordcolumn
