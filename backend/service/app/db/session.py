from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

DATABASE_URL = (
        {f"mysql+pymysql://{settings.DB_USER}:"
        f"{settings.DB_PASSWROD}@{settings.DB_HOST}/"
        f"{settings.DB_NAME}"}
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

#Dependency for FastAPI
def get_db():
    db =  SessionLocal()
    try:
        yield db
    finally:
        db.close()