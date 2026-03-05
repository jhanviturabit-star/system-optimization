from fastapi import FastAPI
from app.api import system

app = FastAPI()

app.include_router(system.router)

@app.get("/")
def root():
    return {"message" : "Welcome!"}
