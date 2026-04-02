from fastapi import FastAPI
from app.Interface.sql_db import dbEngine

app = FastAPI()

@app.get("/")
def root():
    return {"message": "backend is running"}

@app.get("/mqaDB")
def mqaDB():
    with dbEngine.connect() as dbConnection:
        return {"message": "database connected"}