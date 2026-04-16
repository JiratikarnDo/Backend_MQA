import os

from fastapi import Depends, FastAPI
from sqlmodel import Session
from sqlalchemy import text
from app.Interface.sql_db import engine, base, getDb
from app.endpoint.masterdata import router as masterdata_router
from app.endpoint.auth import router as auth_router
from app.endpoint.course import router as course_router
from app.endpoint.subject_category import router as subject_category_router
import uvicorn
import app.models

# from app.models.mqa3 import *

app = FastAPI()

base.metadata.create_all(bind=engine)
app.include_router(masterdata_router)
app.include_router(auth_router)
app.include_router(course_router)
app.include_router(subject_category_router)

@app.get("/")
def root():
    return {"message": "backend is running"}

@app.get("/test-db")
def test_database_connection(db: Session = Depends(getDb)):
    try:
        result = db.execute(text("SELECT VERSION()")).scalar()
        return {"status": "success", "message": f"เชื่อมต่อสำเร็จ! MySQL Version: {result}"}
    except Exception as e:
        return {"status": "error", "message": f"เชื่อมต่อไม่สำเร็จ: {str(e)}"}

if __name__ == "__main__":
    port_env = os.getenv("PORT")

    
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"), 
        port=int(port_env)
    )