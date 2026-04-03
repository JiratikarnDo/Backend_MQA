from fastapi import FastAPI
from app.Interface.sql_db import engine, base
import app.models.masterdata

app = FastAPI()

base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "backend is running"}

@app.get("/testDb")
def testDb():
    with engine.connect() as connection:
        return {"message": "database connected"}