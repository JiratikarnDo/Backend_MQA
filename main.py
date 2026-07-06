import os

from fastapi import Depends, FastAPI
from fastapi.openapi.utils import get_openapi
from sqlmodel import Session
from sqlalchemy import text
from app.Interface.sql_db import engine, base, getDb
from app.endpoint.plo import router as plo_router
from app.endpoint.masterdata import router as masterdata_router
from app.endpoint.auth import router as auth_router
from app.endpoint.course import router as course_router
from app.endpoint.subject_category import router as subject_category_router
from app.endpoint.department import router as department_router
from app.endpoint.curriculum import router as curriculum_router
from app.endpoint.tqf_deadlines import router as tqf_deadlines_router
from app.endpoint.course_opening import router as course_opening_router
from app.endpoint.course_assignment import router as course_assignment_router
from app.endpoint.tqf3 import router as tqf_router
from app.endpoint.tqf5 import router as tqf5_router
from app.endpoint.user import router as users_router
from app.endpoint.word_import import router as word_import_router
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import app.models

# from app.models.mqa3 import *

app = FastAPI()

origins_raw = os.getenv("FRONTEND_URL") or os.getenv("FRONEND_URL")
origins = origins_raw.split(",") if origins_raw else []

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

base.metadata.create_all(bind=engine)


app.include_router(masterdata_router)
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(course_router)
app.include_router(subject_category_router)
app.include_router(department_router)
app.include_router(curriculum_router)
app.include_router(plo_router)
app.include_router(tqf_deadlines_router)
app.include_router(course_opening_router)
app.include_router(course_assignment_router)
app.include_router(word_import_router)
app.include_router(tqf_router)
app.include_router(tqf5_router)


def fix_binary_file_schema(value):
    if isinstance(value, dict):
        if value.get("contentMediaType") == "application/octet-stream":
            value.pop("contentMediaType", None)
            value["format"] = "binary"

        for child in value.values():
            fix_binary_file_schema(child)

    if isinstance(value, list):
        for child in value:
            fix_binary_file_schema(child)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
    )
    fix_binary_file_schema(openapi_schema)
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


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
        host=os.getenv("HOST"),
        port=int(port_env)
    )
