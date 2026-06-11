from psycopg2 import sql

def insert_into_table(cursor, table_name, data):
    if hasattr(data, "model_dump"):
        data = data.model_dump()

    columns = list(data.keys())
    values = list(data.values())

    query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
        sql.Identifier(table_name),

        sql.SQL(", ").join([
            sql.Identifier(column)
            for column in columns
        ]),

        sql.SQL(", ").join([
            sql.Placeholder()
            for _ in values
        ])
    )

    cursor.execute(query, values)