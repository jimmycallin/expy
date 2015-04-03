db_user = "root"
db_password = None

try:
    import pymysql as db
    if db_password:
        database_url = 'mysql+pymysql://{}:{}@localhost/expy'.format(db_user, db_password)
    else:
        database_url = 'mysql+pymysql://{}@localhost/expy'.format(db_user)
except ImportError:
    import sqlite as db
    database_url = 'sqlite://:memory:'

