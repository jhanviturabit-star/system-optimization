from pydantic import BaseModel
from typing import Optional, Dict

class TaskRequest(BaseModel):
    system_id: int
    action: str
    payload: Optional[Dict] = {}

task_queue = {}