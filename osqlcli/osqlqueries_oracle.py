def get_schemas():
    """
    Query string to retrieve schema names.
    :return: string
    """
    return '''select username as name from all_users'''


def get_databases():
    """
    Query string to retrieve all database names.
    :return: string
    """
    return '''
        Select "databasename" as name from dual'''


def get_table_columns():
    """
    Query string to retrieve all table columns.
    :return: string
    """
    return '''select t.owner as table_schema,t.table_name, t.column_name, t.data_type, t.data_default as column_default 
            from all_tab_columns t, all_tables
            where t.table_name = all_tables.table_name'''


def get_view_columns():
    """
    Query string to retrieve all view columns.
    :return: string
    """
    return '''select t.owner as table_schema,t.table_name, t.column_name, t.data_type, t.data_default as column_default 
            from all_tab_columns t, all_views
            where t.table_name = all_views.view_name'''


def get_views():
    """
    Query string to retrieve all views.
    :return: string
    """
    return '''select owner as table_schema, view_name as table_name from all_views'''


def get_tables():
    """
    Query string to retrive all tables.
    :return: string
    """
    return '''select owner as table_schema, table_name as table_name from all_tables'''


def get_user_defined_types():
    """
    Query string to retrieve all user defined types.
    :return: string
    """
    return '''select owner as schemas_dot_name, type_name as types_dot_name from ALL_TYPES'''


def get_functions():
    """
    Query string to retrieve stored procedures and functions.
    :return: string
    """
    return """
	select owner as specific_schema, object_name as specific_name from all_objects where object_type = 'FUNCTION'"""


def get_foreignkeys():
    """
    Query string for returning foreign keys.
    :return: string
    """
    return """
	select p.owner AS fk_table_schema,p.table_name AS fk_table_name,'fk_column_name' AS fk_column_name,
		p.r_owner AS referenced_table_schema,c.table_name AS referenced_table_name,'referenced_column_name' AS referenced_column_name
	from all_constraints p, all_constraints c
	where p.constraint_type='R'
	and p.r_constraint_name = c.constraint_name
	and c.constraint_type in ('P','U')"""
