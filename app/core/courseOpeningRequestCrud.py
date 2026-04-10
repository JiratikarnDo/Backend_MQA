from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.dbmodels.courseOpeningRequest import courseOpeningRequest


STATUS_DRAFT = "draft"
STATUS_PENDING_APPROVAL = "pendingApproval"
STATUS_REJECTED = "rejected"
STATUS_APPROVED = "approved"

VALID_STATUSES = {
    STATUS_DRAFT,
    STATUS_PENDING_APPROVAL,
    STATUS_REJECTED,
    STATUS_APPROVED,
}

CREATABLE_STATUSES = {STATUS_DRAFT, STATUS_PENDING_APPROVAL}
EDITABLE_STATUSES = {STATUS_DRAFT, STATUS_REJECTED}

VALID_DEGREE_LEVELS = {"bachelor", "master", "doctoral"}
VALID_REQUEST_SCOPES = {"inMajor", "outMajor"}


def normalizeStatus(status: str | None):
    if not status:
        return STATUS_DRAFT
    normalized = status.strip()
    if normalized == "submitted":
        return STATUS_PENDING_APPROVAL
    return normalized


def normalizeConfirmStatus(confirmStatus: str | None):
    if not confirmStatus:
        return "notConfirm"
    return confirmStatus.strip()


def validateStatus(status: str):
    if status not in VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"invalid status: {status}"
        )


def validateDegreeLevel(degreeLevel: str):
    if degreeLevel not in VALID_DEGREE_LEVELS:
        raise HTTPException(
            status_code=400,
            detail=f"invalid degreeLevel: {degreeLevel}"
        )


def validateRequestScope(requestScope: str):
    if requestScope not in VALID_REQUEST_SCOPES:
        raise HTTPException(
            status_code=400,
            detail=f"invalid requestScope: {requestScope}"
        )


def ensureEditableStatus(status: str, actionName: str):
    if status not in EDITABLE_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"cannot {actionName} when status is '{status}'"
        )


def extractSummaryFields(documentData: dict):
    generalForm = documentData.get("generalForm", {}) if documentData else {}

    return {
        "semester": generalForm.get("semester"),
        "academicYear": generalForm.get("academicYear"),
        "curriculumName": generalForm.get("curriculumName"),
        "majorName": generalForm.get("majorName"),
    }


def ensureUserMajor(userMajor: str | None):
    if not userMajor or not userMajor.strip():
        raise HTTPException(
            status_code=400,
            detail="user major is required"
        )
    return userMajor.strip()


def applyUserMajorToDocumentData(documentData: dict, userMajor: str):
    payload = dict(documentData or {})
    generalForm = dict(payload.get("generalForm") or {})
    generalForm["majorName"] = userMajor
    payload["generalForm"] = generalForm
    return payload


def createCourseOpeningRequest(db: Session, requestData, userMajor: str):
    status = normalizeStatus(requestData.status)
    confirmStatus = normalizeConfirmStatus(getattr(requestData, "confirmStatus", None))
    userMajor = ensureUserMajor(userMajor)

    validateStatus(status)
    validateDegreeLevel(requestData.degreeLevel)
    validateRequestScope(requestData.requestScope)

    if status not in CREATABLE_STATUSES:
        raise HTTPException(
            status_code=400,
            detail="new document can be created only with status 'draft' or 'pendingApproval'"
        )

    documentData = applyUserMajorToDocumentData(requestData.documentData, userMajor)
    summaryFields = extractSummaryFields(documentData)

    newRequest = courseOpeningRequest(
        degreeLevel=requestData.degreeLevel,
        requestScope=requestData.requestScope,
        status=status,
        confirmStatus=confirmStatus,
        documentData=documentData,
        semester=summaryFields["semester"],
        academicYear=summaryFields["academicYear"],
        curriculumName=summaryFields["curriculumName"],
        majorName=summaryFields["majorName"],
    )

    db.add(newRequest)
    db.commit()
    db.refresh(newRequest)
    return newRequest


def getCourseOpeningRequestList(
    db: Session,
    userMajor: str,
    degreeLevel: str | None = None,
    requestScope: str | None = None,
    statusValue: str | None = None,
    semester: str | None = None,
    academicYear: str | None = None,
):
    userMajor = ensureUserMajor(userMajor)
    query = db.query(courseOpeningRequest)

    query = query.filter(courseOpeningRequest.majorName == userMajor)

    if degreeLevel:
        query = query.filter(courseOpeningRequest.degreeLevel == degreeLevel)

    if requestScope:
        query = query.filter(courseOpeningRequest.requestScope == requestScope)

    if statusValue:
        query = query.filter(courseOpeningRequest.status == statusValue)

    if semester:
        query = query.filter(courseOpeningRequest.semester == semester)

    if academicYear:
        query = query.filter(courseOpeningRequest.academicYear == academicYear)

    return query.order_by(courseOpeningRequest.id.desc()).all()


def getCourseOpeningRequestDetail(db: Session, requestId: int, userMajor: str):
    userMajor = ensureUserMajor(userMajor)
    requestItem = (
        db.query(courseOpeningRequest)
        .filter(courseOpeningRequest.id == requestId)
        .filter(courseOpeningRequest.majorName == userMajor)
        .first()
    )

    if not requestItem:
        raise HTTPException(status_code=404, detail="courseOpeningRequest not found")

    return requestItem


def updateCourseOpeningRequest(db: Session, requestId: int, requestData, userMajor: str):
    userMajor = ensureUserMajor(userMajor)
    requestItem = (
        db.query(courseOpeningRequest)
        .filter(courseOpeningRequest.id == requestId)
        .filter(courseOpeningRequest.majorName == userMajor)
        .first()
    )

    if not requestItem:
        raise HTTPException(status_code=404, detail="courseOpeningRequest not found")

    ensureEditableStatus(requestItem.status, "update")

    nextStatus = normalizeStatus(requestData.status)
    nextConfirmStatus = normalizeConfirmStatus(getattr(requestData, "confirmStatus", None))

    validateStatus(nextStatus)
    validateDegreeLevel(requestData.degreeLevel)
    validateRequestScope(requestData.requestScope)

    if requestItem.status == STATUS_DRAFT and nextStatus not in {STATUS_DRAFT, STATUS_PENDING_APPROVAL}:
        raise HTTPException(
            status_code=400,
            detail="draft can change only to 'draft' or 'pendingApproval'"
        )

    if requestItem.status == STATUS_REJECTED and nextStatus not in {STATUS_REJECTED, STATUS_PENDING_APPROVAL}:
        raise HTTPException(
            status_code=400,
            detail="rejected can change only to 'rejected' or 'pendingApproval'"
        )

    documentData = applyUserMajorToDocumentData(requestData.documentData, userMajor)
    summaryFields = extractSummaryFields(documentData)

    requestItem.degreeLevel = requestData.degreeLevel
    requestItem.requestScope = requestData.requestScope
    requestItem.status = nextStatus
    requestItem.confirmStatus = nextConfirmStatus
    requestItem.documentData = documentData
    requestItem.semester = summaryFields["semester"]
    requestItem.academicYear = summaryFields["academicYear"]
    requestItem.curriculumName = summaryFields["curriculumName"]
    requestItem.majorName = summaryFields["majorName"]

    db.commit()
    db.refresh(requestItem)
    return requestItem


def deleteCourseOpeningRequest(db: Session, requestId: int, userMajor: str):
    userMajor = ensureUserMajor(userMajor)
    requestItem = (
        db.query(courseOpeningRequest)
        .filter(courseOpeningRequest.id == requestId)
        .filter(courseOpeningRequest.majorName == userMajor)
        .first()
    )

    if not requestItem:
        raise HTTPException(status_code=404, detail="courseOpeningRequest not found")

    if requestItem.status != STATUS_DRAFT:
        raise HTTPException(
            status_code=400,
            detail=f"cannot delete when status is '{requestItem.status}'"
        )

    db.delete(requestItem)
    db.commit()

    return {"message": "courseOpeningRequest deleted successfully"}
