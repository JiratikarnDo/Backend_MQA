from pydantic import BaseModel
from typing import List, Optional

class SubPLOResponse(BaseModel):
    id: int
    sub_plo_code: str
    sub_plo_name_thai: str
    courses: List[dict] = [] 
    
    model_config = {"from_attributes": True}

class PLOResponse(BaseModel):
    id: int
    plo_code: str
    plo_name_thai: str
    sub_plos: List[SubPLOResponse] = []

    model_config = {"from_attributes": True}

class SubPLOCreate(BaseModel):
    sub_plo_code: str
    sub_plo_name_thai: str
    plo_id: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "sub_plo_code": "PLO1.1",
                "sub_plo_name_thai": "สามารถเขียนอัลกอริทึมพื้นฐานได้",
                "plo_id": 1
            }
        }
    }