from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.system_schema import SystemCreate
from app.models.system import System
from app.db.session import get_db

router = APIRouter()

router.post("/system/register")
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