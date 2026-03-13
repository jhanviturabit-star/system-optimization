from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from ..schemas.system_schema import SystemCreate
from service.app.models.system import System
from ..db.session import get_db
from service.app.schemas.metrics_schema import SystemMetrics

router = APIRouter()

@router.post("/system/register")
def register_system(system: SystemCreate, db: Session = Depends(get_db)):
    new_system = System(
        hostname = system.hostname,
        os = system.os
    )

    db.add(new_system)
    db.commit()
    db.refresh(new_system)

    return {
        "message": "System registered successfully",
        "system_id": new_system.id
    }

@router.post("/system/report")
def report_metrics(metrics: SystemMetrics, db: Session = Depends(get_db)):

    db.execute(
        text(""" 
        CALL insert_system_metrics(
            :system_id,
            :cpu,
            :ram,
            :disk,
            :temp,
            :startup
        )
        """),
        {
            "system_id": metrics.system_id,
            "cpu": metrics.cpu_usage,
            "ram": metrics.ram_usage,
            "disk": metrics.disk_usage,
            "temp": metrics.temp_size_mb,
            "startup": metrics.startup_files
        }
    )

    db.commit()

    return {"message" : "Metrics recorded successfully"}
    
@router.get("/system/status/{system_id}")
def get_system_status(system_id: int, db: Session = Depends (get_db)):
    """
    Triggers current health of the system & returns the data needed for the Streamlit guages.
    """

    db.execute(text("CALL calculate_health_score(:system_id)"), {"system_id": system_id})
    db.commit()

    query = text("SELECT cpu_usage, disk_usage, ram_usage, health_score FROM latest_system_metrics WHERE system_id = :system_id")
    result = db.execute(query, {"system_id": system_id}).fetchone()

    if result:
        return {
            "cpu_usage": result[0],
            "ram_usage": result[2],
            "disk_usage": result[1],
            "health_score": result[3]
        }
    return {"message": "No metrics found for this system"}

@router.get("/system")
def get_systems(db: Session = Depends(get_db)):
    
    query = text(""" 
        SELECT id, hostname, os
        FROM systems
    """)

    result = db.execute(query).fetchall()

    systems = []

    for row in result:
        systems.append({
            "id": row[0],
            "system_name": row[1],
            "os": row[2]
        })

    return {"systems": systems}