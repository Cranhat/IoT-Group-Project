from fastapi import APIRouter, Depends, HTTPException

from database.src.database import Database, TABLE_MODELS
from database.src.db_fetch import fetch_table
from database.src.db_insert import insert_into_table
from database.src.db_update import update_table


router = APIRouter(prefix="/tables", tags=["tables"])

db_instance = Database()


@router.get("/{table}")
def get_table(table: str, db=Depends(db_instance.get_db)):
    db_instance.validate_table(table)

    conn, curr = db
    data = fetch_table(curr, table)

    return {
        "table": table,
        "data": data,
    }


@router.get("/{table}/{id}")
def get_row_by_id(table: str, id: int, db=Depends(db_instance.get_db)):
    db_instance.validate_table(table)

    conn, curr = db

    curr.execute(f"SELECT * FROM {table} WHERE id = %s", (id,))
    data = curr.fetchone()

    if not data:
        raise HTTPException(status_code=404, detail="Not found")

    return {
        "table": table,
        "id": id,
        "data": data,
    }


@router.post("/{table}")
def insert(table: str, payload: dict, db=Depends(db_instance.get_db)):
    db_instance.validate_table(table)

    Model = TABLE_MODELS.get(table)

    try:
        validated_data = Model(**payload)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    conn, curr = db

    try:
        insert_into_table(curr, table, validated_data)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "message": f"{table} inserted successfully",
    }


@router.put("/{table}/{id}")
def update(table: str, id: int, payload: dict, db=Depends(db_instance.get_db)):
    db_instance.validate_table(table)

    Model = TABLE_MODELS.get(table)

    try:
        validated_data = Model(**payload)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    conn, curr = db

    try:
        update_table(curr, table, validated_data, {"id": id})
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "message": f"{table} updated successfully",
    }