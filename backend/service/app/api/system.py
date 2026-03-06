from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..schemas.system_schema import SystemCreate
from service.app.models.system import System
from ..db.session import get_db

from sqlalchemy import text
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
            "startup": metrics.startup_programs
        }
    )

    db.commit()

    return {"message" : "Metrics recorded successfully"}