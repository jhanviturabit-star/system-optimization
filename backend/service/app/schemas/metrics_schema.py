from pydantic import BaseModel

class SystemMetrics(BaseModel):
    system_id: int
    cpu_usage: float
    ram_usage: float
    disk_usage: float
    temperature: float
    startup_time: int
