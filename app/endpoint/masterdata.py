from fastapi import APIRouter
from app.utils.rmutto_api import fetch_from_rmutto

router = APIRouter() 

@router.get("/teachers")
async def get_teachers():
    result = await fetch_from_rmutto(action="teachers")
    return result