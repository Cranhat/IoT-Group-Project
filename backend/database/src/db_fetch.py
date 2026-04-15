from psycopg2 import sql

def fetch_table(cursor, table_name):   
    query = sql.SQL("SELECT * FROM {table}").format(
        table=sql.Identifier(table_name),
    )

    cursor.execute(query)
    return cursor.fetchall()

def fetch_table_where(cursor, table_name, where: dict):
    where_columns = [sql.Identifier(k) + sql.SQL(" = ") + sql.Placeholder() for k in where.keys()]
    
    query = sql.SQL("SELECT * FROM {table} WHERE {where_fields}").format(
        table=sql.Identifier(table_name),
        where_fields=sql.SQL(" AND ").join(where_columns)
    )

    values = list(where.values())
    cursor.execute(query, values)
    return cursor.fetchall()
