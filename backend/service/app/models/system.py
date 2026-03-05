from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.sql import func
from app.db.base import Base

class System(Base):
    __tablename__ = "systems"

    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String(100), nullable=False)
    os = Column(String(100))
    registered_at = Column(TIMESTAMP, server_default=func.now())

    