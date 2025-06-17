from django.db.backends.oracle.base import DatabaseWrapper as OracleDatabaseWrapper
import cx_Oracle
from conf.env import DATABASE_HOST, DATABASE_PORT, DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD

class DatabaseWrapper(OracleDatabaseWrapper):
    def get_new_connection(self, conn_params):
        host = DATABASE_HOST
        port = DATABASE_PORT
        name = DATABASE_NAME
        user = DATABASE_USER
        password = DATABASE_PASSWORD

        dsn = cx_Oracle.makedsn(
            host,
            port,
            service_name=name
        )
        # Remove any existing 'dsn' key to avoid conflicts
        conn_params['dsn'] = dsn

        # Pass the connection parameters to the superclass method without 'dsn'
        return cx_Oracle.connect(
            user=user,
            password=password,
            dsn=dsn,
            threaded=True,
            encoding="UTF-8",
            nencoding="UTF-8"
        )