import psycopg2
from psycopg2 import pool
from flask import current_app, g

class BaseRepository:

    """ PostgreSQL """

    _pool = None

    @classmethod
    def initialize_pool(cls):
        if cls._pool is None:
            cls._pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=current_app.config['DB_HOST'],
                port=current_app.config['DB_PORT'],
                database=current_app.config['DB_NAME'],
                user=current_app.config['DB_USER'],
                password=current_app.config['DB_PASSWORD']
            )

    @classmethod
    def get_db_connection(cls):
        if 'db_conn' not in g:
            if cls._pool is None:
                cls.initialize_pool()
            g.db_conn = cls._pool.getconn()
        return g.db_conn

    @classmethod
    def release_connection(cls):
        conn = g.pop('db_conn', None)
        if conn is not None and cls._pool is not None:
            cls._pool.putconn(conn)
