from osqlcli.main import OsqlCli
from osqltestutils import create_osql_cli_options


DEFAULT_OPTIONS = create_osql_cli_options()
DEFAULT = OsqlCli(DEFAULT_OPTIONS).row_limit
LIMIT = DEFAULT + 1000

low_count = 1
over_default = DEFAULT + 1
over_limit = LIMIT + 1


def test_default_row_limit():
    cli = OsqlCli(DEFAULT_OPTIONS)
    stmt = "SELECT * FROM students"
    result = cli._should_show_limit_prompt(stmt, ['row']*low_count)
    assert result is False

    result = cli._should_show_limit_prompt(stmt, ['row']*over_default)
    assert result is True


def test_set_row_limit():
    cli_options = create_osql_cli_options(row_limit=LIMIT)
    cli = OsqlCli(cli_options)
    stmt = "SELECT * FROM students"
    result = cli._should_show_limit_prompt(stmt, ['row']*over_default)
    assert result is False

    result = cli._should_show_limit_prompt(stmt, ['row']*over_limit)
    assert result is True


def test_no_limit():
    cli_options = create_osql_cli_options(row_limit=0)
    cli = OsqlCli(cli_options)
    assert cli.row_limit is 0
    stmt = "SELECT * FROM students"

    result = cli._should_show_limit_prompt(stmt, ['row']*over_limit)
    assert result is False


def test_row_limit_on_non_select():
    cli = OsqlCli(DEFAULT_OPTIONS)
    stmt = "UPDATE students set name='Boby'"
    result = cli._should_show_limit_prompt(stmt, None)
    assert result is False

    cli_options = create_osql_cli_options(row_limit=0)
    assert cli_options.row_limit is 0
    cli = OsqlCli(cli_options)
    result = cli._should_show_limit_prompt(stmt, ['row']*over_default)
    assert cli.row_limit is 0
    assert result is False
