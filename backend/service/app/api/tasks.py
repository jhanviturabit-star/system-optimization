from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from service.app.db.session import get_db
from sqlalchemy import text
from pydantic import BaseModel

class TaskStatusUpdate(BaseModel):
    task_id: int
    status: str 

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.get("/{system_id}")
def get_tasks(system_id: int, db: Session = Depends(get_db)):
    query = text(""" 
        SELECT id, action_type, payload_json
        FROM optimization_queue
        WHERE system_id = :system_id
        AND status = 'pending'
    """)

    result = db.execute(query, {"system_id": system_id}).fetchall()

    tasks = []

    for row in result:
        tasks.append({
            "task_id": row.id,
            "action": row.action_type,

        })
        
    return {"tasks": tasks}

@router.post("/update-status")
def update_task_status(data: TaskStatusUpdate, db: Session = Depends(get_db)):
    query = text(""" 
        UPDATE optimization_queue
        SET status = :status
        WHERE id = :task_id    
    """)
    
    db.execute(query, {
        "status": data.status,
        "task_id": data.task_id
    })

    db.commit()

    return {"message": "Task status updated"}