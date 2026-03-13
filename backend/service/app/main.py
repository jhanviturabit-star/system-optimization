from fastapi import FastAPI
from service.app.api import system, tasks, metrics, processes

app = FastAPI()

app.include_router(system.router)
app.include_router(tasks.router)
app.include_router(metrics.router)
app.include_router(processes.router)

@app.get("/")
def root():
    return {"message" : "Welcome!"}



