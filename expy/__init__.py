from . import config
from .config import db

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
PRIMARY KEY (id),

CONSTRAINT `TestDataProject_fk_1`
    FOREIGN KEY (project_name) 
    REFERENCES Project(name)
    ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ExperimentResult
(
experiment_id int(11) NOT NULL,
instance_id int(11) NOT NULL,
predicted text,
PRIMARY KEY (experiment_id, instance_id),

CONSTRAINT `ExperimentResultExperiment_fk_1`
    FOREIGN KEY (experiment_id) 
    REFERENCES Experiment(id)
    ON DELETE CASCADE,

CONSTRAINT `ExperimentResultTestData_fk_1`
    FOREIGN KEY (instance_id) 
    REFERENCES TestData(id)
    ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Tag
(
experiment_id int(11) NOT NULL,
tag varchar(255) NOT NULL,
PRIMARY KEY (experiment_id, tag),

CONSTRAINT `TagExperiment_fk_1`
    FOREIGN KEY (experiment_id) 
    REFERENCES Experiment(id)
    ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Configuration
(
experiment_id int(11) NOT NULL,
parameter varchar(255) NOT NULL,
value text,
PRIMARY KEY (experiment_id, parameter),

CONSTRAINT `ConfigurationExperiment_fk_1`
    FOREIGN KEY (experiment_id) 
    REFERENCES Experiment(id)
    ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Experiment
(
id int(11) NOT NULL AUTO_INCREMENT,
project_name varchar(255) NOT NULL,
description text,
`commit` text,
`timestamp` datetime,
PRIMARY KEY (id),

CONSTRAINT `ExperimentProject_fk_1`
    FOREIGN KEY (project_name) 
    REFERENCES Project(name)
    ON DELETE CASCADE
);
"""

cursor = db.connect(user=config.db_user, passwd=config.db_password).cursor()
cursor.execute(create_database + sql)

from .project import Project

projects = Project.get_projects()