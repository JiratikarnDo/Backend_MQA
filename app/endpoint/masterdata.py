from fastapi import APIRouter
from app.utils.rmutto_api import fetch_from_rmutto

router = APIRouter() 

@router.get("/test-api")
async def test_rmutto_api(action: str):
    result = await fetch_from_rmutto(action=action)
    return result