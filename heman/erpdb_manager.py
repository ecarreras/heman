import os
import psycopg2
from urlparse import urlparse


def get_timescale_connection():
    url = os.environ.get('POSTGRESQL_URI')
    psql = urlparse(url)
    user = psql.username
    password = psql.password
    dbname = psql.path[1:]
    host = psql.hostname
    port = psql.port

    return psycopg2.connect(
        host=host,
        dbname=dbname,
        user=user,
        port=port,
        password=password
    )
