from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class TQFDeadlineCreate(BaseModel):
    tqf_type: str = Field(..., examples=["มคอ.3"])
    semester: int = Field(..., examples=[1])
    academic_year: int = Field(..., examples=[2569])
    start_date: datetime = Field(..., examples=["2026-06-01T08:30:00"])
    end_date: datetime = Field(..., examples=["2026-06-30T16:30:00"])

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tqf_type": "มคอ.3",
                "semester": 1,
                "academic_year": 2569,
                "start_date": "2026-06-01T00:00:00",
                "end_date": "2026-06-15T23:59:59"
            }
        }
    )

class TQFDeadlineCreate(BaseModel):
    tqf_type: str = Field(..., examples=["มคอ.3"])
    semester: int = Field(..., examples=[1])
    academic_year: int = Field(..., examples=[2569])
    
    start_date: datetime = Field(..., examples=["2026-06-01T00:00:00"])
    end_date: datetime = Field(..., examples=["2026-06-30T23:59:59"])

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tqf_type": "มคอ.3",
                "semester": 1,
                "academic_year": 2569,
                "start_date": "2026-06-01T00:00:00",
                "end_date": "2026-06-30T23:59:59"
            }
        }
    )


class TQFDeadlineResponse(BaseModel):
    id: int
    tqf_type: str
    semester: int
    academic_year: int
    start_date: datetime
    end_date: datetime
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)