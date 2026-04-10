from fastapi import FastAPI
from app.Interface.sql_db import engine, base
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

@app.get("/testDb")
def testDb():
    with engine.connect() as connection:
        return {"message": "database connected"}
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
