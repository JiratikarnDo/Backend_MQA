from fastapi import Depends, FastAPI
from sqlmodel import Session, text
from app.Interface.sql_db import engine, base, getDb
import app.models.masterdata
import app.dbmodels.courseOpeningRequest
from app.endpoint.masterdata import router as masterdata_router
from app.endpoint.courseOpeningRequest import router as course_opening_request_router

app = FastAPI()

base.metadata.create_all(bind=engine)
app.include_router(masterdata_router)
app.include_router(course_opening_request_router, prefix="/api/headMajor")

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
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
