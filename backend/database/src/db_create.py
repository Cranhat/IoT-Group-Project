from psycopg2 import sql

ALLOWED_TABLES = {"users", "passwords", "devices", "task_logs"}

def insert_into_table(cursor, table_name, data):
    if table_name not in ALLOWED_TABLES:
        raise ValueError("Invalid table name")
    
    if hasattr(data, "model_dump"):
        data = data.model_dump()

    columns = data.keys()
    values = list(data.values())

    query = sql.SQL("INSERT INTO {table} ({fields}) VALUES ({placeholders})").format(
        table=sql.Identifier(table_name),
        fields=sql.SQL(", ").join(map(sql.Identifier, columns)),
        placeholders=sql.SQL(", ").join(sql.Placeholder() * len(values))
    )

    cursor.execute(query, values)