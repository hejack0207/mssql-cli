# coding=utf-8
from __future__ import unicode_literals
import os
import tempfile

from time import sleep

from osqltestutils import (
    create_osql_cli,
    create_osql_cli_options,
    create_osql_cli_client,
    shutdown
)
from osqlcli.osql_cli import OutputSettings, MssqlFileHistory


def test_history_file_not_store_credentials():
    # Used by prompt tool kit, verify statements that contain password or secret
    # are not stored by the history file.
    statements = [
        'Create Database Scoped Credential With Password = <secret>',
        'CREATE MASTER KEY WITH SECRET=xyz',
    ]

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file_path = temp_file.name
        file_history = MssqlFileHistory(temp_file_path)

        for statement in statements:
            file_history.append(statement)

    assert len(file_history) == 0


def test_format_output():
    osqlcli = create_osql_cli()
    settings = OutputSettings(table_format='psql', dcmlfmt='d', floatfmt='g')
    results = osqlcli.format_output('Title',
                                     [('abc', 'def')],
                                     ['head1', 'head2'],
                                     'test status',
                                     settings)
    expected = [
        'Title',
        '+---------+---------+',
        '| head1   | head2   |',
        '|---------+---------|',
        '| abc     | def     |',
        '+---------+---------+',
        'test status'
    ]
    assert list(results) == expected


def test_format_output_live_connection():
    sleep(7)
    statement = u"""
        select 1 as [ShiftID], 'Day' as [Name] UNION ALL
        select 2, N'魚' UNION ALL
        select 3, 'Night'
    """
    try:
        osqlcli = create_osql_cli()
        result = run_and_return_string_from_formatter(osqlcli, statement)
        expected = [
            u'+-----------+--------+',
            u'| ShiftID   | Name   |',
            u'|-----------+--------|',
            u'| 1         | Day    |',
            u'| 2         | 魚     |',
            u'| 3         | Night  |',
            u'+-----------+--------+',
            u'(3 rows affected)'
        ]
        assert list(result) == expected
    finally:
        shutdown(osqlcli.osqlcliclient_main)


def test_format_output_expanded_live_connection():
    statement = u"""
        select N'配列' as [Name] UNION ALL
        select 'Evening' UNION ALL
        select 'Night'
    """

    try:
        osqlcli = create_osql_cli()
        result = run_and_return_string_from_formatter(osqlcli, statement, expanded=True)

        expected = [
            '-[ RECORD 1 ]-------------------------',
            'Name | 配列',
            '-[ RECORD 2 ]-------------------------',
            'Name | Evening',
            '-[ RECORD 3 ]-------------------------',
            'Name | Night',
            '(3 rows affected)'
            ]
        assert list(result) == expected
    finally:
        shutdown(osqlcli.osqlcliclient_main)


def test_format_output_auto_expand():
    osqlcli = create_osql_cli()
    settings = OutputSettings(
        table_format='psql',
        dcmlfmt='d',
        floatfmt='g',
        max_width=100)
    table_results = osqlcli.format_output('Title',
                                           [('abc', 'def')],
                                           ['head1', 'head2'],
                                           'test status',
                                           settings)
    table = [
        'Title',
        '+---------+---------+',
        '| head1   | head2   |',
        '|---------+---------|',
        '| abc     | def     |',
        '+---------+---------+',
        'test status'
    ]
    assert list(table_results) == table
    expanded_results = osqlcli.format_output(
        'Title',
        [('abc', 'def')],
        ['head1', 'head2'],
        'test status',
        settings._replace(max_width=1)
    )
    expanded = [
        'Title',
        '-[ RECORD 1 ]-------------------------',
        'head1 | abc',
        'head2 | def',
        'test status'
    ]
    assert list(expanded_results) == expanded


def test_missing_rc_dir(tmpdir):
    try:
        rcfile = str(tmpdir.join("subdir").join("rcfile"))
        osqlcli = create_osql_cli(osqlclirc_file=rcfile)
        assert os.path.exists(rcfile)
    finally:
        osqlcli.sqltoolsclient.shutdown()


def run_and_return_string_from_formatter(osql_cli, sql, join=False, expanded=False):
    """
    Return string output for the sql to be run.
    """
    osql_cli.connect_to_database()
    osql_cli_client = osql_cli.osqlcliclient_main
    for rows, col, message, query, is_error in osql_cli_client.execute_query(sql):
        settings = OutputSettings(table_format='psql',
                                  dcmlfmt='d',
                                  floatfmt='g',
                                  expanded=expanded)
        formatted = osql_cli.format_output(None, rows, col, message, settings)
        if join:
            formatted = '\n'.join(formatted)

        return formatted
