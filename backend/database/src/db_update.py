from psycopg2 import sql

ALLOWED_TABLES = {"users", "passwords", "devices", "task_logs", "task_result_logs", "http_logs"}

def update_table(cursor, table_name, data, where: dict):
    if table_name not in ALLOWED_TABLES:
        raise ValueError("Invalid table name")
    
    if hasattr(data, "model_dump"):
        data = data.model_dump()
    
    set_columns = [sql.Identifier(k) + sql.SQL(" = ") + sql.Placeholder() for k in data.keys()]
    
    where_columns = [sql.Identifier(k) + sql.SQL(" = ") + sql.Placeholder() for k in where.keys()]
    
    query = sql.SQL("UPDATE {table} SET {set_fields} WHERE {where_fields}").format(
        table=sql.Identifier(table_name),
        set_fields=sql.SQL(", ").join(set_columns),
        where_fields=sql.SQL(" AND ").join(where_columns)
    )
    
    values = list(data.values()) + list(where.values())
    
    cursor.execute(query, values)