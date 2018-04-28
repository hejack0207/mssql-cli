import argparse
import osqlcli
import os

from .config import config_location

OSQL_CLI_USER = u'OSQL_CLI_USER'
OSQL_CLI_PASSWORD = u'OSQL_CLI_PASSWORD'
OSQL_CLI_DATABASE = u'OSQL_CLI_DATABASE'
OSQL_CLI_SERVER = u'OSQL_CLI_SERVER'
OSQL_CLI_PORT = u'OSQL_CLI_PORT'
OSQL_CLI_ROW_LIMIT = u'OSQL_CLI_ROW_LIMIT'
OSQL_CLI_RC = u'OSQL_CLI_RC'


def create_parser():
    args_parser = argparse.ArgumentParser(
        prog=u'osql-cli',
        description=u'Omni SQL CLI. ' +
        u'Version {}'.format(osqlcli.__version__))

    args_parser.add_argument(
        u'-U', u'--username',
        dest=u'username',
        default=os.environ.get(OSQL_CLI_USER, None),
        metavar=u'',
        help=u'Username to connect to the database')

    args_parser.add_argument(
        u'-P', u'--password',
        dest=u'password',
        default=os.environ.get(OSQL_CLI_PASSWORD, None),
        metavar=u'',
        help=u'If not supplied, defaults to value in environment variable OSQL_CLI_PASSWORD.')

    args_parser.add_argument(
        u'-d', u'--database',
        dest=u'database',
        default=os.environ.get(OSQL_CLI_DATABASE, u'master'),
        metavar=u'',
        help=u'database name to connect to.')

    args_parser.add_argument(
        u'-S', u'--server',
        dest=u'server',
        default=os.environ.get(OSQL_CLI_SERVER, u'localhost'),
        metavar=u'',
        help=u'SQL Server instance name or address.')

    args_parser.add_argument(
        u'-p', u'--port',
        dest=u'port',
        default=os.environ.get(OSQL_CLI_PORT, u'1521'),
        metavar=u'',
        help=u'service tcp(/udp) port number.')

    args_parser.add_argument(
        u'-v', u'--version',
        dest=u'version',
        action=u'store_true',
        default=False,
        help=u'Version of osql-cli.')

    args_parser.add_argument(
        u'--osqlclirc',
        dest=u'osqlclirc_file',
        default=os.environ.get(OSQL_CLI_RC, config_location() + 'config'),
        metavar=u'',
        help=u'Location of osqlclirc config file.')

    args_parser.add_argument(
        u'--row-limit',
        dest=u'row_limit',
        default=os.environ.get(OSQL_CLI_ROW_LIMIT, None),
        metavar=u'',
        help=u'Set threshold for row limit prompt. Use 0 to disable prompt.')

    args_parser.add_argument(
        u'--less-chatty',
        dest=u'less_chatty',
        action=u'store_true',
        default=False,
        help=u'Skip intro on startup and goodbye on exit.')

    args_parser.add_argument(
        u'-l', u'--connect-timeout',
        dest=u'connection_timeout',
        default=0,
        metavar=u'',
        help=u'Time in seconds to wait for a connection to the server before terminating request.')

    args_parser.add_argument(
        u'--prompt',
        dest=u'prompt',
        metavar=u'',
        help=u'Prompt format (Default: \\d> ')

    return args_parser
