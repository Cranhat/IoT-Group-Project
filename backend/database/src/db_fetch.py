from psycopg2 import sql

def fetch_table(cursor, table_name: str):
    query = sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name))

    cursor.execute(query)

    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()

    return [dict(zip(columns, row)) for row in rows]


def fetch_table_where(cursor, table_name: str, where: dict):
    if not where:
        return fetch_table(cursor, table_name)

    where_fields = [
        sql.SQL("{} = {}").format(
            sql.Identifier(column),
            sql.Placeholder()
        )
        for column in where.keys()
    ]

    query = sql.SQL("SELECT * FROM {} WHERE {}").format(
        sql.Identifier(table_name),
        sql.SQL(" AND ").join(where_fields)
    )

    values = list(where.values())

    cursor.execute(query, values)

    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()

    return [dict(zip(columns, row)) for row in rows]
