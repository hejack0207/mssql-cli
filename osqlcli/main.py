from __future__ import unicode_literals
from __future__ import print_function

import click
import getpass
import os
import sys
import platform

from builtins import input

from osqlcli.config import config_location
from osqlcli.__init__ import __version__


click.disable_unicode_literals_warning = True

try:
    from urlparse import urlparse, unquote, parse_qs
except ImportError:
    from urllib.parse import urlparse, unquote, parse_qs

from osqlcli.osql_cli import OsqlCli
from osqlcli.osqlclioptionsparser import create_parser


def run_cli_with(options):

    create_config_dir_for_first_use()

    display_version_message(options)

    osqlcli = OsqlCli(options)
    osqlcli.connect_to_database()

    osqlcli.run()


def create_config_dir_for_first_use():
    config_dir = os.path.dirname(config_location())
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
        return True

    return False


def display_version_message(options):
    if options.version:
        print('Version:', __version__)
        sys.exit(0)

if __name__ == "__main__":
    osqlcli_options_parser = create_parser()
    osqlcli_options = osqlcli_options_parser.parse_args(sys.argv[1:])
    run_cli_with(osqlcli_options)
