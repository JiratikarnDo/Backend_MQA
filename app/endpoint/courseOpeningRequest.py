from typing import Optional
from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.Interface.sql_db import getDb
from app.models.courseOpeningRequest import (
    courseOpeningRequestCreate,
    courseOpeningRequestResponse,
)
from app.core.courseOpeningRequestCrud import (
    createCourseOpeningRequest,
    getCourseOpeningRequestList,
    getCourseOpeningRequestDetail,
    updateCourseOpeningRequest,
    deleteCourseOpeningRequest,
)

router = APIRouter(prefix="/courseOpeningRequest", tags=["headMajor"])


def getUserMajorHeader(
    x_user_major: str = Header(
        ...,
        alias="X-User-Major",
        description="Current user's major name. Example: วิทยาการคอมพิวเตอร์",
    )
):
    return x_user_major


@router.post("", response_model=courseOpeningRequestResponse)
async def createCourseOpeningRequestApi(
    requestData: courseOpeningRequestCreate,
    userMajor: str = Depends(getUserMajorHeader),
    db: Session = Depends(getDb)
):
    result = createCourseOpeningRequest(db=db, requestData=requestData, userMajor=userMajor)
    return result


@router.get("", response_model=list[courseOpeningRequestResponse])
async def getCourseOpeningRequestListApi(
    degreeLevel: Optional[str] = None,
    requestScope: Optional[str] = None,
    statusValue: Optional[str] = None,
    semester: Optional[str] = None,
    academicYear: Optional[str] = None,
    userMajor: str = Depends(getUserMajorHeader),
    db: Session = Depends(getDb)
):
    result = getCourseOpeningRequestList(
        db=db,
        userMajor=userMajor,
        degreeLevel=degreeLevel,
        requestScope=requestScope,
        statusValue=statusValue,
        semester=semester,
        academicYear=academicYear,
    )
    return result


@router.get("/{requestId}", response_model=courseOpeningRequestResponse)
async def getCourseOpeningRequestDetailApi(
    requestId: int,
    userMajor: str = Depends(getUserMajorHeader),
    db: Session = Depends(getDb)
):
    result = getCourseOpeningRequestDetail(db=db, requestId=requestId, userMajor=userMajor)
    return result


@router.put("/{requestId}", response_model=courseOpeningRequestResponse)
async def updateCourseOpeningRequestApi(
    requestId: int,
    requestData: courseOpeningRequestCreate,
    userMajor: str = Depends(getUserMajorHeader),
    db: Session = Depends(getDb)
):
    result = updateCourseOpeningRequest(
        db=db,
        requestId=requestId,
        requestData=requestData,
        userMajor=userMajor,
    )
    return result


@router.delete("/{requestId}")
async def deleteCourseOpeningRequestApi(
    requestId: int,
    userMajor: str = Depends(getUserMajorHeader),
    db: Session = Depends(getDb)
):
    result = deleteCourseOpeningRequest(db=db, requestId=requestId, userMajor=userMajor)
    return result
