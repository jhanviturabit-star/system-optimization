from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..db.session import get_db

router = APIRouter()

@router.get("/system/metrics/{system_id}")
def get_metrics(system_id: int, db: Session = Depends(get_db)):

    query = text("""
        SELECT cpu_usage, ram_usage, disk_usage, temp_size_mb, created_at
        FROM system_metrics
        WHERE system_id = :system_id
        ORDER BY created_at DESC
        LIMIT 20
    """)

    result = db.execute(query, {"system_id": system_id}).fetchall()

    metrics = []
    for row in result:
        metrics.append({
            "cpu_usage": row[0],
            "ram_usage": row[1],
            "disk_usage": row[2],
            "temp_size_mb": row[3],
            "created_at": str(row[4])
        })

    return {"metrics": metrics}
