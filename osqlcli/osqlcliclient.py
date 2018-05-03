
import click
import copy
import logging
import sqlparse
import time
import uuid

from osqlcli.packages import special
from osqlcli.packages.parseutils.meta import ForeignKey
from time import sleep

logger = logging.getLogger(u'osqlcli.osqlcliclient')
time_wait_if_no_response = 0.05


def generate_owner_uri():
    return u'osql-cli-' + uuid.uuid4().urn


class OsqlCliClient(object):

    def __init__(self, osqlcli_options, owner_uri=None, **kwargs):

        self.dbms=osqlcli_options.dbms
        self.db_ip=osqlcli_options.server
        self.port=osqlcli_options.port
        self.sid=osqlcli_options.instance
        self.db_user=osqlcli_options.username
        self.db_password=osqlcli_options.password

    def connect_to_database(self):
        if "oracle" == self.dbms:
            import cx_Oracle
            from osqlcli import osqlqueries_oracle as osqlqueries
            self.conn=cx_Oracle.connect(self.db_user,self.db_password,"{}/{}".format(self.db_ip,self.sid))
        elif "sqlite" == self.dbms:
            import sqlite3
            from osqlcli import osqlqueries_sqlite as osqlqueries
            self.conn=sqlite3.connect("/tmp/database")

        self.osqlqry = osqlqueries
        return "conn_str",None

    def execute_query(self, query):

        # Try to run first as special command
        try:
            for rows, columns, status, statement, is_error in special.execute(self, query):
                yield rows, columns, status, statement, is_error
        except special.CommandNotFound:
            # Execute as normal sql
            # Remove spaces, EOL and semi-colons from end
            query = query.strip()
            if not query:
                yield None, None, None, query, False
            else:
                for single_query in sqlparse.split(query):
                    # Remove spaces, EOL and semi-colons from end
                    single_query = single_query.strip().rstrip(';')
                    if single_query:
                        for rows, columns, status, statement, is_error in self._execute_query(single_query):
                            yield rows, columns, status, statement, is_error
                    else:
                        yield None, None, None, None, False
                        continue

    def _execute_query(self, query):
        curs = self.conn.cursor()
        curs.execute(query)
        colnames = [desc[0] for desc in curs.description]
        rows = []
        for row in curs.fetchall():
            rows.append(row)

        yield rows, colnames, None, query, False

    def clone(self):
        cloned_osqlcli_client = copy.copy(self)
        cloned_osqlcli_client.owner_uri = generate_owner_uri()
        cloned_osqlcli_client.is_connected = False

        return cloned_osqlcli_client

    def get_schemas(self):
        """ Returns a list of schema names"""
        query = self.osqlqry.get_schemas()
        logger.info(u'Schemas query: {0}'.format(query))
        for tabular_result in self.execute_query(query):
            return [x[0] for x in tabular_result[0]]

    def get_databases(self):
        """ Returns a list of database names"""
        query = self.osqlqry.get_databases()
        logger.info(u'Databases query: {0}'.format(query))
        for tabular_result in self.execute_query(query):
            return [x[0] for x in tabular_result[0]]

    def get_tables(self):
        """ Yields (schema_name, table_name) tuples"""
        query = self.osqlqry.get_tables()
        logger.info(u'Tables query: {0}'.format(query))
        for tabular_result in self.execute_query(query):
            for row in tabular_result[0]:
                yield (row[0], row[1])

    def get_table_columns(self):
        """ Yields (schema_name, table_name, column_name, data_type, column_default) tuples"""
        query = self.osqlqry.get_table_columns()
        logger.info(u'Table columns query: {0}'.format(query))
        for tabular_result in self.execute_query(query):
            for row in tabular_result[0]:
                yield (row[0], row[1], row[2], row[3], row[4])

    def get_views(self):
        """ Yields (schema_name, table_name) tuples"""
        query = self.osqlqry.get_views()
        logger.info(u'Views query: {0}'.format(query))
        for tabular_result in self.execute_query(query):
            for row in tabular_result[0]:
                yield (row[0], row[1])

    def get_view_columns(self):
        """ Yields (schema_name, table_name, column_name, data_type, column_default) tuples"""
        query = self.osqlqry.get_view_columns()
        logger.info(u'View columns query: {0}'.format(query))
        for tabular_result in self.execute_query(query):
            for row in tabular_result[0]:
                yield (row[0], row[1], row[2], row[3], row[4])

    def get_user_defined_types(self):
        """ Yields (schema_name, type_name) tuples"""
        query = self.osqlqry.get_user_defined_types()
        logger.info(u'UDTs query: {0}'.format(query))
        for tabular_result in self.execute_query(query):
            for row in tabular_result[0]:
                yield (row[0], row[1])

    def get_foreign_keys(self):
        """ Yields (parent_schema, parent_table, parent_column, child_schema, child_table, child_column) typles"""
        query = self.osqlqry.get_foreignkeys()
        logger.info(u'Foreign keys query: {0}'.format(query))
        for tabular_result in self.execute_query(query):
            for row in tabular_result[0]:
                yield ForeignKey(*row)

    def shutdown(self):
        logger.info(u'Shutdown OsqlCliClient')
        self.conn.close()
