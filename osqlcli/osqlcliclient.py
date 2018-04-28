
import click
import copy
import logging
import sqlparse
import time
import uuid

from osqlcli import osqlqueries
from osqlcli.packages import special
from osqlcli.packages.parseutils.meta import ForeignKey
from time import sleep

from sqlalchemy import create_engine
from sqlalchemy.sql import text

logger = logging.getLogger(u'osqlcli.osqlcliclient')
time_wait_if_no_response = 0.05


def generate_owner_uri():
    return u'osql-cli-' + uuid.uuid4().urn


class OsqlCliClient(object):

    def __init__(self, osqlcli_options, owner_uri=None, **kwargs):

        self.db_ip=osqlcli_options.server
        self.port=osqlcli_options.port
        self.sid=osqlcli_options.database
        self.db_user=osqlcli_options.username
        self.db_password=osqlcli_options.password

        self.conn_str='oracle+cx_oracle://'+self.db_user+':'+self.db_password+'@'+self.db_ip+':'+str(self.port)+'/'+self.sid
        if self.db_user == 'SYS' or self.db_user == 'sys' :
            self.conn_str += '?mode=2'

        logger.info(u'Initialized OsqlCliClient with owner Uri {}'.format(self.conn_str))

    def get_base_connection_params(self):
        return {u'ServerName': self.db_ip,
                u'DatabaseName': self.sid,
                u'UserName': self.db_user,
                u'Password': self.db_password,
                u'OwnerUri': self.conn_str
                }

    def connect_to_database(self):
        self.engine = create_engine(self.conn_str, echo=False)
        self.conn = self.engine.connect()

    def execute_query(self, query):
        s=text(query)
        r = self.conn.execute(s)
        rdata = r.fetchall()
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
        pass

    def clone(self, sqltoolsclient=None):
        cloned_osqlcli_client = copy.copy(self)
        cloned_osqlcli_client.owner_uri = generate_owner_uri()
        cloned_osqlcli_client.is_connected = False

        if sqltoolsclient:
            cloned_osqlcli_client.sql_tools_client = sqltoolsclient

        return cloned_osqlcli_client

    def _generate_query_results_to_tuples(self, query, message, column_info=None, result_rows=None, is_error=False):
        # Returns a generator of rows, columns, status(rows affected) or
        # message, sql (the query), is_error
        if is_error:
            return (), None, message, query, is_error

        columns = [col.column_name for col in column_info] if column_info else None

        rows = ([[cell.display_value for cell in result_row.result_cells]
                 for result_row in result_rows]) if result_rows else ()

        return rows, columns, message, query, is_error

    def get_schemas(self):
        """ Returns a list of schema names"""
        query = osqlqueries.get_schemas()
        logger.info(u'Schemas query: {0}'.format(query))
        for tabular_result in self.execute_query(query):
            return [x[0] for x in tabular_result[0]]

    def get_databases(self):
        """ Returns a list of database names"""
        query = osqlqueries.get_databases()
        logger.info(u'Databases query: {0}'.format(query))
        for tabular_result in self.execute_query(query):
            return [x[0] for x in tabular_result[0]]

    def get_tables(self):
        """ Yields (schema_name, table_name) tuples"""
        query = osqlqueries.get_tables()
        logger.info(u'Tables query: {0}'.format(query))
        for tabular_result in self.execute_query(query):
            for row in tabular_result[0]:
                yield (row[0], row[1])

    def get_table_columns(self):
        """ Yields (schema_name, table_name, column_name, data_type, column_default) tuples"""
        query = osqlqueries.get_table_columns()
        logger.info(u'Table columns query: {0}'.format(query))
        for tabular_result in self.execute_query(query):
            for row in tabular_result[0]:
                yield (row[0], row[1], row[2], row[3], row[4])

    def get_views(self):
        """ Yields (schema_name, table_name) tuples"""
        query = osqlqueries.get_views()
        logger.info(u'Views query: {0}'.format(query))
        for tabular_result in self.execute_query(query):
            for row in tabular_result[0]:
                yield (row[0], row[1])

    def get_view_columns(self):
        """ Yields (schema_name, table_name, column_name, data_type, column_default) tuples"""
        query = osqlqueries.get_view_columns()
        logger.info(u'View columns query: {0}'.format(query))
        for tabular_result in self.execute_query(query):
            for row in tabular_result[0]:
                yield (row[0], row[1], row[2], row[3], row[4])

    def get_user_defined_types(self):
        """ Yields (schema_name, type_name) tuples"""
        query = osqlqueries.get_user_defined_types()
        logger.info(u'UDTs query: {0}'.format(query))
        for tabular_result in self.execute_query(query):
            for row in tabular_result[0]:
                yield (row[0], row[1])

    def get_foreign_keys(self):
        """ Yields (parent_schema, parent_table, parent_column, child_schema, child_table, child_column) typles"""
        query = osqlqueries.get_foreignkeys()
        logger.info(u'Foreign keys query: {0}'.format(query))
        for tabular_result in self.execute_query(query):
            for row in tabular_result[0]:
                yield ForeignKey(*row)

    def shutdown(self):
        self.conn.close()
        logger.info(u'Shutdown OsqlCliClient')