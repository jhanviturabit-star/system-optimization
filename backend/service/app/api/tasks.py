from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from service.app.db.session import get_db
from sqlalchemy import text
from pydantic import BaseModel
import json

class TaskStatusUpdate(BaseModel):
    task_id: int
    status: str 

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/create")
def create_task(system_id: int, action_type: str, payload: str=None, db: Session = Depends(get_db)):

    payload_json = payload if payload else "{}"

    try:
        db.execute(
            text("CALL add_optimization_task(:system_id, :action_type, :payload)"),
            {"system_id": system_id, "action_type": action_type, "payload": payload_json}
        )
        db.commit()
        return {"message": "Task created successfully"}
    except Exception as e:
        db.rollback()
        print(f"Db error: {e}")
        return {"message": f"Error creating task: {str(e)}"}, 500

@router.get("/{system_id}")
def get_tasks(system_id: int, db: Session = Depends(get_db)):
    query = text(""" 
        SELECT id, action_type, payload_json
        FROM optimization_queue
        WHERE system_id = :system_id
        AND status = 'pending'
    """)

    #payload = None

    result = db.execute(query, {"system_id": system_id}).fetchall()

    tasks = []

    for row in result:
        tasks.append({
            "task_id": row[0],
            "action": row[1],
            "payload": row[2]
            #"created_at": str(row.created_at) if hasattr(row, "created_at") else None
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

@router.post("/{task_id}/complete")
def complete_task(task_id: int, db: Session = Depends(get_db)):
    
    db.execute(
        text(""" 
        UPDATE optimization_queue
        SET status = 'completed'
        WHERE id = :task_id
        """),
        {"task_id": task_id}
    )

    # db.execute(query, {"task_id": task_id})
    db.commit()

    return {"message": "Task completed"}