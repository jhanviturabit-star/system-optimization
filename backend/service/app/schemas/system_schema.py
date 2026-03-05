from pydantic import BaseModel

class SystemCreate(BaseModel):
    hostname : str
    os : str

    