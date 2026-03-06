from fastapi import FastAPI
from service.app.api import system, tasks

app = FastAPI()

app.include_router(system.router)
app.include_router(tasks.router)


@app.get("/")
def root():
    return {"message" : "Welcome!"}

