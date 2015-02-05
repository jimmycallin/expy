import pymysql

create_database = "CREATE DATABASE IF NOT EXISTS expy; USE expy;"

sql = """
CREATE TABLE IF NOT EXISTS Project
(
name varchar(255) NOT NULL,
description text,
project_path text,
PRIMARY KEY (name)
);

CREATE TABLE IF NOT EXISTS TestData
(
id int(11) NOT NULL AUTO_INCREMENT,
instance text NOT NULL,
answer text NOT NULL,
project_name varchar(255) NOT NULL,
PRIMARY KEY (id)
);

ALTER TABLE TestData ADD INDEX (project_name);

CREATE TABLE IF NOT EXISTS ExperimentResult
(
experiment_id int(11) NOT NULL,
instance_id int(11) NOT NULL,
predicted text NOT NULL,
PRIMARY KEY (experiment_id, instance_id)
);

CREATE TABLE IF NOT EXISTS Tag
(
experiment_id int(11) NOT NULL,
tag varchar(255) NOT NULL,
PRIMARY KEY (experiment_id, tag)
);

CREATE TABLE IF NOT EXISTS Configuration
(
experiment_id int(11) NOT NULL,
parameter varchar(255) NOT NULL,
value text,
PRIMARY KEY (experiment_id, parameter)
);

CREATE TABLE IF NOT EXISTS Experiment
(
id int(11) NOT NULL AUTO_INCREMENT,
project_name varchar(255) NOT NULL,
description text,
`commit` text,
`timestamp` datetime,
PRIMARY KEY (id)
);
"""

cursor = pymysql.connect(user='root').cursor()
cursor.execute(create_database + sql)

from .project import Project