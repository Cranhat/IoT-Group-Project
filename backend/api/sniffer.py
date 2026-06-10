from fastapi import APIRouter, Depends, HTTPException, Query

from database.src.database import Database

router = APIRouter(tags=["sniffer"])

db_instance = Database()


@router.get("/sniffer/logs")
def get_sniffer_logs(
    limit: int = Query(10, ge=1, le=100),
    sort: str = Query("desc"),
    db=Depends(db_instance.get_db),
):
    conn, curr = db

    if sort not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Sort must be asc or desc")

    try:
        curr.execute(
            f"""
            SELECT sniffer_name, port, log, timestamp
            FROM packet_sniffer_logs
            ORDER BY timestamp {sort.upper()}
            LIMIT %s;
            """,
            (limit,),
        )

        rows = curr.fetchall()

        logs = [
            {
                "sniffer_name": row[0],
                "port": row[1],
                "log": row[2],
                "timestamp": row[3],
            }
            for row in rows
        ]

        return {"logs": logs}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))