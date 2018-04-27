import osqlcli.sqltoolsclient as sqltoolsclient
import osqlcli.osqlcliclient as osqlcliclient

from argparse import Namespace
from osqlcli.osql_cli import osqlCli
from osqlcli.osqlclioptionsparser import create_parser


def create_osql_cli(**non_default_options):
    osqlcli_options = create_osql_cli_options(**non_default_options)
    osql_cli = osqlCli(osqlcli_options)

    return osql_cli


def create_osql_cli_client(options=None, owner_uri=None, connect=True, sql_tools_client=None, **additional_params):
    """
    Retrieve a osqlcliclient connection.
    :param options: options
    :param owner_uri: string
    :param connect: boolean
    :param sql_tools_client: SqlToolsClient
    :param additional_params: kwargs
    :return: osqlCliClient
    """
    try:
        sql_tools_client = sql_tools_client if sql_tools_client else sqltoolsclient.SqlToolsClient()
        osql_cli_options = options if options else create_osql_cli_options()

        osql_cli_client = osqlcliclient.osqlCliClient(osql_cli_options,
                                                         sql_tools_client,
                                                         owner_uri=owner_uri,
                                                         **additional_params)

        if connect:
            osql_cli_client.connect_to_database()
        return osql_cli_client
    except Exception as e:
        print('Connection failed')
        raise e


def create_osql_cli_options(**nondefault_options):

    parser = create_parser()

    default_osql_cli_options = parser.parse_args('')

    if nondefault_options:
        updateable_osql_cli_options = vars(default_osql_cli_options)
        for option in nondefault_options.keys():
            if option not in updateable_osql_cli_options.keys():
                raise Exception('Invalid osql-cli option specified: {}'.format(option))

            updateable_osql_cli_options[option] = nondefault_options.get(option)

        return Namespace(**updateable_osql_cli_options)

    return default_osql_cli_options


def shutdown(connection):
    connection.shutdown()
