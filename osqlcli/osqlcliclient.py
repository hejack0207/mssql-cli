
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

    def __init__(self, osqlcli_options, sql_tools_client, owner_uri=None, **kwargs):

        self.db_ip=osqlcli_options.db_ip
        self.port=osqlcli_options.port
        self.sid=osqlcli_options.sid
        self.db_user=osqlcli_options.db_user
        self.db_password=osqlcli_options.db_password

        self.conn_str='oracle+cx_oracle://'+self.db_user+':'+self.db_password+'@'+self.db_ip+':'+str(self.port)+'/'+self.sid
        if self.db_user == 'SYS' or self.db_user == 'sys' :
            conn_str += '?mode=2'

        logger.info(u'Initialized OsqlCliClient with owner Uri {}'.format(self.owner_uri))

    def get_base_connection_params(self):
        return {u'ServerName': self.server_name,
                u'DatabaseName': self.database,
                u'UserName': self.user_name,
                u'Password': self.password,
                u'AuthenticationType': self.authentication_type,
                u'OwnerUri': self.owner_uri
                }

    def connect_to_database(self):
        self.engine = create_engine(self.conn_str, echo=False)
        self.conn = self.engine.connect()

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
        query_response, query_messages, query_had_error = self._execute_query_execute_request_for(query)

        if self._exception_found_in(query_response):
            yield self._generate_query_results_to_tuples(query=query,
                                                         message=query_response.exception_message,
                                                         is_error=query_had_error)
            return

        if self._no_results_found_in(query_response) or self._no_rows_found_in(query_response):
            query_message = query_messages[0].message if query_messages else u''
            yield self._generate_query_results_to_tuples(query=query,
                                                         message=query_message,
                                                         is_error=query_had_error)
        else:
            query_subset_responses_and_summaries = self._execute_query_subset_request_for(query_response)

            for query_subset_response, result_set_summary, query_subset_error in query_subset_responses_and_summaries:
                if self._error_message_found_in(query_subset_response):
                    yield self._generate_query_results_to_tuples(query=query,
                                                                 message=query_subset_response.error_message,
                                                                 is_error=query_subset_error)

                query_message_for_current_result_set = query_messages[result_set_summary.id].message \
                    if query_messages else u''

                yield self._generate_query_results_to_tuples(column_info=result_set_summary.column_info,
                                                             result_rows=query_subset_response.rows,
                                                             query=query,
                                                             message=query_message_for_current_result_set)

    def clone(self, sqltoolsclient=None):
        cloned_osqlcli_client = copy.copy(self)
        cloned_osqlcli_client.owner_uri = generate_owner_uri()
        cloned_osqlcli_client.is_connected = False

        if sqltoolsclient:
            cloned_osqlcli_client.sql_tools_client = sqltoolsclient

        return cloned_osqlcli_client

    def _execute_connection_request_with(self, connection_params):
        if self.is_connected:
            return self.owner_uri, []

        connection_request = self.sql_tools_client.create_request(self.sql_tools_client.CONNECTION_REQUEST,
                                                                  connection_params,
                                                                  self.owner_uri)
        connection_request.execute()
        error_messages = []
        response = None

        while not connection_request.completed():
            response = connection_request.get_response()

            if isinstance(response, connectionservice.ConnectionCompleteEvent):
                if response.error_message:
                    error_messages.append(u'Error message: {}'.format(response.error_message))
                if response.messages:
                    logger.error(response.messages)
            else:
                time.sleep(time_wait_if_no_response)

        if response and response.connection_id:
            assert response.owner_uri == self.owner_uri
            self.is_connected = True
            self.server_version = response.server_version
            self.server_edition = response.server_edition
            self.is_cloud = response.is_cloud

            logger.info(
                u'Connection Successful. Connection Id {0}'.format(
                    response.connection_id))

            return self.owner_uri, error_messages

        return None, error_messages

    def _execute_query_execute_request_for(self, query):
        if not self.is_connected:
            click.secho(u'No connection established with the server.',
                        err=True,
                        fg='yellow')
            exit(1)

        query_request = self.sql_tools_client.create_request(self.sql_tools_client.QUERY_EXECUTE_STRING_REQUEST,
                                                             {u'OwnerUri': self.owner_uri,
                                                              u'Query': query},
                                                             self.owner_uri)
        query_request.execute()
        query_response = None
        query_messages = []
        while not query_request.completed():
            query_response = query_request.get_response()
            if isinstance(query_response, queryservice.QueryMessageEvent):
                query_messages.append(query_response)
            else:
                sleep(time_wait_if_no_response)

        query_has_exception = query_response.exception_message
        query_has_error_messages = query_messages[0].is_error if query_messages else False
        query_has_batch_error = query_response.batch_summaries[0].has_error \
            if hasattr(query_response, 'batch_summaries') else False

        query_failed = query_has_exception or query_has_batch_error or query_has_error_messages

        return query_response, query_messages, query_failed

    def _execute_query_subset_request_for(self, query_response):
        subset_responses_and_summaries = []
        for result_set_summary in query_response.batch_summaries[0].result_set_summaries:
            query_subset_request = self.sql_tools_client.create_request(self.sql_tools_client.QUERY_SUBSET_REQUEST,
                                                                        {u'OwnerUri': query_response.owner_uri,
                                                                         u'BatchIndex': result_set_summary.batch_id,
                                                                         u'ResultSetIndex': result_set_summary.id,
                                                                         u'RowsStartIndex': 0,
                                                                         u'RowCount': result_set_summary.row_count},
                                                                        self.owner_uri)

            query_subset_request.execute()

            query_subset_response = None
            while not query_subset_request.completed():
                query_subset_response = query_subset_request.get_response()
                if not query_subset_response:
                    sleep(time_wait_if_no_response)

            query_subset_had_error = query_subset_request.error_message \
                if hasattr(query_subset_request, 'error_message') else False

            subset_responses_and_summaries.append((query_subset_response, result_set_summary, query_subset_had_error))

        return subset_responses_and_summaries


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
