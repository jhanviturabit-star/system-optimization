from fastapi import FastAPI
from service.app.api import system, tasks, metrics

app = FastAPI()

app.include_router(system.router)
app.include_router(tasks.router)
app.include_router(metrics.router)

@app.get("/")
def root():
    return {"message" : "Welcome!"}



