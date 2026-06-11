from psycopg2 import sql

def update_table(cursor, table_name, data, where: dict):
    if hasattr(data, "model_dump"):
        data = data.model_dump()

    set_columns = [
        sql.SQL("{} = {}").format(
            sql.Identifier(key),
            sql.Placeholder()
        )
        for key in data.keys()
    ]

    where_columns = [
        sql.SQL("{} = {}").format(
            sql.Identifier(key),
            sql.Placeholder()
        )
        for key in where.keys()
    ]

    query = sql.SQL("UPDATE {} SET {} WHERE {}").format(
        sql.Identifier(table_name),
        sql.SQL(", ").join(set_columns),
        sql.SQL(" AND ").join(where_columns)
    )
    
    values = list(data.values()) + list(where.values())

    cursor.execute(query, values)