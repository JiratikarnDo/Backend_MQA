import os
import httpx
from dotenv import load_dotenv

load_dotenv()

async def fetch_from_rmutto(action: str, acadyear: str = None, semester: str = None, classid: str = None):
    url = os.getenv("RMUTTO_API_URL")
    params = {
        "username": os.getenv("RMUTTO_API_USERNAME"),
        "password": os.getenv("RMUTTO_API_PASSWORD"),
        "secretkey": os.getenv("RMUTTO_API_SECRETKEY"),
        "action": action
    }
    
    if action == "courses" and acadyear and semester and classid:
        params["acadyear"] = acadyear
        params["semester"] = semester
        params["classid"] = classid
    elif action in ["teacherschedule", "studentenroll"] and classid:
        params["classid"] = classid

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, dict) and "error" in data:
                    return {"success": False, "error": data["error"]}
                    
                return {"success": True, "data": data}
            else:
                return {"success": False, "error": f"HTTP Error: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}