from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.Interface.sql_db import getDb
from app.dependencies.auth import check_admin_staff_role
from app.endpoint.course import (
    SubjectDocxPayload,
    resolveDepartmentId,
    saveSubjectPayload,
    subjectPayloadToResponse,
)
from app.models.courses import Courses
from app.models.users import Users
from app.services.docxImportService import extractCoursesFromDocx
from app.services.wordConvertService import convertWordFileToDocxBytes

router = APIRouter(prefix="/word-import", tags=["Word Import"])


def isCourseCode15(courseCode: Optional[str]) -> bool:
    cleanCode = str(courseCode or "").strip().replace(" ", "").replace("–", "-")
    return cleanCode.startswith("15")


def findExistingSubject(
    db: Session,
    payload: SubjectDocxPayload,
    currentUser: Users,
) -> Optional[Courses]:
    departmentId = resolveDepartmentId(db, payload.departmentId, currentUser)
    courseCode = str(payload.courseCode or "").strip()

    if not courseCode:
        raise HTTPException(status_code=400, detail="ไม่พบรหัสวิชา")

    return (
        db.query(Courses)
        .filter(
            Courses.course_code == courseCode,
            Courses.department_id == departmentId,
        )
        .first()
    )


async def importSubjectsFromWordFiles(
    files: List[UploadFile],
    courseLevel: str,
    departmentId: Optional[int],
    db: Session,
    current_user: Users,
    onlyCode15: bool,
) -> dict:
    if not files:
        raise HTTPException(status_code=400, detail="กรุณาอัปโหลดไฟล์ .doc หรือ .docx อย่างน้อย 1 ไฟล์")

    if len(files) > 2:
        raise HTTPException(status_code=400, detail="อัปโหลดไฟล์ได้สูงสุด 2 ไฟล์เท่านั้น")

    importedSubjects = []
    skippedSubjects = []
    fileResults = []
    createdCount = 0
    skippedExistingCount = 0
    skippedFilteredCount = 0

    try:
        for file in files:
            if not file.filename:
                continue

            if file.filename.startswith("~$"):
                raise HTTPException(
                    status_code=400,
                    detail=f"ไฟล์ {file.filename} เป็นไฟล์ชั่วคราวของ Microsoft Word กรุณาเลือกไฟล์จริง",
                )

            if not file.filename.lower().endswith((".doc", ".docx")):
                raise HTTPException(
                    status_code=400,
                    detail=f"ไฟล์ {file.filename} ไม่ใช่ไฟล์ .doc หรือ .docx",
                )

            fileBytes = await file.read()

            if not fileBytes:
                raise HTTPException(status_code=400, detail=f"ไฟล์ {file.filename} ว่าง")

            docxBytes = convertWordFileToDocxBytes(fileBytes, file.filename)
            extractedCourses = extractCoursesFromDocx(docxBytes)
            fileImportedCount = 0
            fileSkippedExistingCount = 0
            fileSkippedFilteredCount = 0

            for extractedCourse in extractedCourses:
                isCode15 = isCourseCode15(extractedCourse.get("courseCode"))

                if onlyCode15 != isCode15:
                    skippedFilteredCount += 1
                    fileSkippedFilteredCount += 1
                    continue

                extractedCourse["curriculumLevel"] = (
                    courseLevel
                    or extractedCourse.get("curriculumLevel")
                    or "bachelor"
                )
                extractedCourse["departmentId"] = departmentId

                payload = SubjectDocxPayload(**extractedCourse)
                existingCourse = findExistingSubject(db, payload, current_user)

                if existingCourse:
                    skippedExistingCount += 1
                    fileSkippedExistingCount += 1
                    skippedSubjects.append(
                        subjectPayloadToResponse(existingCourse, payload.model_dump())
                    )
                    continue

                course, _ = saveSubjectPayload(db, payload, current_user)
                createdCount += 1
                fileImportedCount += 1
                importedSubjects.append(subjectPayloadToResponse(course, payload.model_dump()))

            fileResults.append(
                {
                    "fileName": file.filename,
                    "courseCount": len(extractedCourses),
                    "importedCount": fileImportedCount,
                    "skippedExistingCount": fileSkippedExistingCount,
                    "skippedFilteredCount": fileSkippedFilteredCount,
                }
            )

        db.commit()

        return {
            "message": "นำเข้ารายวิชา จาก Word สำเร็จ" if onlyCode15 else "นำเข้ารายวิชาจาก Word สำเร็จ",
            "mode": "code15Only" if onlyCode15 else "excludeCode15",
            "createdCount": createdCount,
            "skippedExistingCount": skippedExistingCount,
            "skippedFilteredCount": skippedFilteredCount,
            "totalCount": len(importedSubjects),
            "fileResults": fileResults,
            "subjects": importedSubjects,
            "skippedSubjects": skippedSubjects,
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"เกิดข้อผิดพลาดในการนำเข้าไฟล์ Word: {str(error)}",
        )


@router.post("/courses")
async def import_subjects_from_docx(
    files: List[UploadFile] = File(...),
    courseLevel: str = Form("bachelor"),
    departmentId: Optional[int] = Form(None),
    db: Session = Depends(getDb),
    current_user: Users = Depends(check_admin_staff_role),
):
    return await importSubjectsFromWordFiles(
        files=files,
        courseLevel=courseLevel,
        departmentId=departmentId,
        db=db,
        current_user=current_user,
        onlyCode15=False,
    )


@router.post("/code-15")
async def import_code15_subjects_from_docx(
    files: List[UploadFile] = File(...),
    courseLevel: str = Form("bachelor"),
    departmentId: Optional[int] = Form(None),
    db: Session = Depends(getDb),
    current_user: Users = Depends(check_admin_staff_role),
):
    return await importSubjectsFromWordFiles(
        files=files,
        courseLevel=courseLevel,
        departmentId=departmentId,
        db=db,
        current_user=current_user,
        onlyCode15=True,
    )
