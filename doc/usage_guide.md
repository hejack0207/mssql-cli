# Usage Guide
Contents
* [Description](#description)
* [Options](#options)
* [Examples](#examples)
*  [Environment Variables](#environment-variables)
* [Special Commands](#special-commands)

## Description
osql-cli is a new and interactive command line query tool for SQL Server. This open source tool works cross-platform and is a proud member of the dbcli community.

osql-cli provides the following key enhancements over sqlcmd in the Terminal environment:
- T-SQL IntelliSense
- Syntax highlighting
- Pretty formatting for query results, including Vertical Format
- Multi-line edit mode
- Configuration file support

If you encounter any issues, see the[troubleshooting](#troubleshooting_guide.md)section for known issues and workarounds.


## Options
Type **osql-cli --help** to also see these options.

```bash 
$ osql-cli --help
Usage: main.py [OPTIONS]

Options:
    -S, --server TEXT       SQL Server instance name or address.
    -U, --username TEXT     Username to connect to the database.
    -W, --password          Force password prompt.
    -E, --integrated        Use integrated authentication on windows.
    -v, --version           Version of osql-cli.
    -d, --database TEXT     database name to connect to.
    --osqlclirc TEXT       Location of osqlclirc config file.
    --row-limit INTEGER     Set threshold for row limit prompt. Use 0 to disable
                            prompt.
    --less-chatty           Skip intro on startup and goodbye on exit.
    --auto-vertical-output  Automatically switch to vertical output mode if the
                            result is wider than the terminal width.
    --help                  Show this message and exit.
```
      
## Examples
Below are example commands that run against the AdventureWorks database in a localhost server instance. Here is a list of examples:

 * [Connect to a server](#connect-to-a-server)
 * [Exit osql-cli](#exit-osql-cli)
 * [Navigate multiple pages of query result](#navigate-multiple-pages-of-query-result)
 * [Quit a query](#quit-a-query)
 * [Clear screen](#clear-screen)
 * [Toggle multi-line mode](#toggle-multi-line-mode)

### Connect to a server
Connect to a server, a specific database, and with a username. -S -d and -U are optional. You can [set environment variables](#Environment-Variables) to set default settings.

```bash
osql-cli -S localhost -d AdventureWorks -U sa
```

### Exit osql-cli 
Press **Ctrl+D** or type:
```bash
quit
```

### Navigate multiple pages of query result
If you select a table that has many rows, it may display the results in multiple pages.

- Press **Enter** key to see one row at a time.
- Press **Space bar** to see one page at a time.
- Press **q** to escape from the result view.

### Quit a query
If you are in the middle of writing a query and would like to cancel it, press **Ctrl+C**

### Clear screen
If you want to clear the Terminal view, press **Ctrl+K**

If you want to clear in Command Prompt, press **Ctrl+L**

### Toggle multi-line mode
To enable multi-line mode, press **F3 key**. You can see at bottom of screen if Multiline is on or off.

To use multi-line mode, follow these instruction:

1. Type the beginning of your query.

```sql
SELECT *
```

2. Press **Enter** key and finish our query. You can keep adding lines pressing **Enter** key.

```sql
SELECT *
......FROM "HumanResources"."Department" as hr
```

3. To go back and make changes to your query, navigate with the arrow keys, including up or down.

```sql
SELECT "Name", "DepartmentID"
......FROM "HumanResources"."Department" as hr;
```

4. To execute your multi-line query, add a semi-colon **;** at the end of the last line of your query, then press **Enter** key

```sql
SELECT "Name", "DepartmentID"
......FROM "HumanResources"."Department" as hr;
```

## Environment Variables
Below are a list of environment variables that can be set.
* OSQL_CLI_SERVER - [Set default server](#set-default-server)
* OSQL_CLI_DATABASE - [Set default database](#set-default-database)
* OSQL_CLI_USER - [Set default user](#set-default-user)
* OSQL_CLI_PASSWORD - [Set default password](#set-default-password)
* OSQL_CLI_ROW_LIMIT - [Set default row limit](#set-default-row-limit)

**Important: If you are using macOS or Linux, use 'export' instead of 'set'. 'set' is Windows-only.**

### Set default server
Set environment variable OSQL_CLI_SERVER to set a default SQL Server instance name or address

```bash
set OSQL_CLI_SERVER=localhost
osql-cli
```

### Set default database
Set environment variable OSQL_CLI_DATABASE to set a default database.

```bash
set OSQL_CLI_DATABASE=AdventureWorks
osql-cli -S localhost -U sa
```

### Set default user
Set environment variable OSQL_CLI_USER to set a default user.

```bash
set OSQL_CLI_USER=sa
osql-cli -S localhost -d AdventureWorks
```

### Set default password
Set environment variable OSQL_CLI_PASSWORD to set a default password.

```bash
set OSQL_CLI_PASSWORD=abc123
osql-cli -S localhost -d AdventureWorks -U sa
```

### Set default row limit
Set environment variable OSQL_CLI_ROW_LIMIT to set threshold for row limit prompt. Use 0 to disable prompt.

```bash
set OSQL_CLI_ROW_LIMIT=10
osql-cli -S localhost -U sa
```

## Special Commands
Special commands are meant to make your life easier. They are shortcuts to a lot of commonly performed tasks and queries.
Moreover you can save your own commonly used queries as shortcuts. 

All special commands start with a backslash ('\\') and doing so will bring up an autocomplete with all special commands and their descriptions. 

For more help simply type '\\?' inside the osql-cli prompt to list all the special commands, their usage and description.

```bash
osql-cli>\?
```

Here are a few examples:

### Example 1: List tables
Show all tables which contain foo in their names:
```bash
osql-cli>\lt foo
```
For verbose output:
```bash
osql-cli>\lt+ foo
```


### Example 2: Named queries
Save 'select * from HumanResources.Department' as a named query called 'dept':
```bash
osql-cli>\sn dept select * from "HumanResources"."Department"
```
Run the named query:
```bash
osql-cli>\n dept
```

You can even add parameters to your saved query:
```bash
osql-cli>\sn dept select * from "HumanResources"."Department" where "Name" like '%$1%'
```
Run the named query 'dept' with a parameter:
```bash
osql-cli>\n dept Human
```

### Full list of special commands
Below table summarizes the special commands supported

| Command | Usage | Description
| --- | --- | --- |
|\d   | \d OBJECT                        | List or describe database objects. Calls sp_help.
|\dn  | \dn [name]                       | Delete a named query.                            
|\e   | \e [file]                        | Edit the query with external editor.             
|\ld  | \ld[+] [pattern]                 | List databases.                                  
|\lf  | \lf[+] [pattern]                 | List functions.                                  
|\li  | \li[+] [pattern]                 | List indexes.                                    
|\ll  | \ll[+] [pattern]                 | List logins and associated roles.                                
|\ls  | \ls[+] [pattern]                 | List schemas.                                    
|\lt  | \lt[+] [pattern]                 | List tables.                                     
|\lv  | \lv[+] [pattern]                 | List views.      
|\n   | \n[+] [name] [param1 param2 ...] | List or execute named queries.                                   
|\sf  | \sf FUNCNAME                     | Show a function's definition.                    
|\sn  | \sn name query                   | Save a named query.                              
|help | \?                               | Show this help.                                  

