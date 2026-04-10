from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


# ระดับการศึกษา / ขอบเขตคำขอ / สถานะเอกสาร
degreeLevelType = Literal["bachelor", "master", "doctoral"]
requestScopeType = Literal["inMajor", "outMajor"]
requestStatusType = Literal["draft", "pendingApproval", "rejected", "approved", "submitted"]
confirmStatusType = Literal["notConfirm", "confirmed", "rejected", "approved"]


# ข้อมูลส่วนหัวของเอกสาร เช่น รอบที่ส่ง ภาคการศึกษา ปีการศึกษา หลักสูตร และสาขา
class courseOpeningGeneralForm(BaseModel):
    submissionRound: str  # รอบที่ส่งแบบเปิดรายวิชา ใช้ทุกระดับ
    semester: str  # ภาคการศึกษา ใช้ทุกระดับ
    academicYear: str  # ปีการศึกษา ใช้ทุกระดับ
    curriculumName: str  # ชื่อหลักสูตร ใช้ทุกระดับ
    majorName: str  # ชื่อสาขา/กลุ่มวิชา ใช้ทุกระดับ
    programType: str  # ประเภทหลักสูตร เช่น 4 ปี / เทียบโอน มาจากฟอร์มปริญญาตรี
    studyPlan: str  # แผนการศึกษา มาจากฟอร์มปริญญาโท
    doctoralFormType: str  # รูปแบบหลักสูตรปริญญาเอก เช่น 1.1 / 1.2 มาจากฟอร์มปริญญาเอก
    formType: str  # ชื่อ field สำรองที่หน้าเอกบางจุดอาจใช้แทน doctoralFormType มาจากฟอร์มปริญญาเอก
    campus: str  # วิทยาเขตที่เปิดสอน มาจากฟอร์มปริญญาเอก


# ข้อมูลรูปแบบการเรียนและสถานที่เรียน
class courseOpeningStudyForm(BaseModel):
    learningPeriod: str  # ช่วงเวลาการเรียน เช่น ภาคปกติ / นอกเวลาราชการ มาจากฟอร์มปริญญาตรีและปริญญาโท
    campus: str  # สถานที่เรียน / วิทยาเขต มาจากฟอร์มปริญญาตรีและปริญญาโท
    targetGroup: str  # กลุ่มเป้าหมายของการเปิดสอน มาจากฟอร์มปริญญาตรี
    studyPlan: str  # แผนการศึกษา มาจากฟอร์มปริญญาโท


# ข้อมูลรายวิชาที่จะเปิดสอน 1 แถว
class courseOpeningSubjectRow(BaseModel):
    courseCode: str  # รหัสวิชา
    courseName: str  # ชื่อรายวิชา
    credits: str  # จำนวนหน่วยกิต
    groupCount: str  # จำนวนกลุ่มเรียน
    studentCount: str  # จำนวนนักศึกษา
    isFreeElective: bool = False  # เป็นวิชาเลือกเสรีหรือไม่
    scienceTrack: bool = False  # อยู่ในกลุ่มสายวิทยาศาสตร์หรือไม่
    humanitiesTrack: bool = False  # อยู่ในกลุ่มสายมนุษยศาสตร์หรือไม่
    note: Optional[str] # หมายเหตุเพิ่มเติมของรายวิชา


# ข้อมูลตารางเปิดสอนของแต่ละชั้นปี
class courseOpeningYearBlock(BaseModel):
    yearLevel: str  # ชั้นปี
    entryTerm: str  # ภาค/ปีที่รับเข้า
    academicYear: str  # ปีการศึกษาของตารางนี้
    subjectRows: list[courseOpeningSubjectRow]  # รายวิชาที่เปิดสอนในชั้นปีนี้


# ข้อมูลผู้รับผิดชอบหลักสูตรแต่ละคน
class courseOpeningResponsiblePerson(BaseModel):
    name: str  # ชื่อผู้รับผิดชอบหลักสูตร
    signedDate: date  # วันที่ลงนาม


# ข้อมูลผู้ลงนามและการยืนยันเอกสาร
class courseOpeningApprovalForm(BaseModel):
    responsiblePeople: list[courseOpeningResponsiblePerson]  # รายชื่อผู้รับผิดชอบหลักสูตร
    headName: str  # ชื่อหัวหน้าสาขาวิชา
    headDate: date  # วันที่หัวหน้าสาขาวิชาลงนาม
    deputyDeanName: str  # ชื่อรองคณบดี
    deputyDeanDate: date  # วันที่รองคณบดีลงนาม
    deanName: str  # ชื่อคณบดี
    deanDate: date  # วันที่คณบดีลงนาม
    isConfirmed: bool = False  # ผู้กรอกยืนยันว่าตรวจสอบข้อมูลครบแล้วหรือไม่


# class หลักที่รวมทุกส่วนของฟอร์มเปิดรายวิชาไว้ในก้อนเดียว
class courseOpeningForm(BaseModel):
    generalForm: courseOpeningGeneralForm  # ข้อมูลทั่วไปของเอกสาร
    studyForm: courseOpeningStudyForm  # ข้อมูลรูปแบบการเรียน/สถานที่เรียน
    yearBlocks: list[courseOpeningYearBlock]  # ตารางรายวิชาที่ขอเปิดสอน
    approvalForm: courseOpeningApprovalForm  # ข้อมูลผู้รับผิดชอบและการลงนาม


# alias เดิมสำหรับใช้เป็น documentData ใน request/response
class courseOpeningDocumentData(courseOpeningForm):
    pass


# โครงคำขอหลักที่ใช้ตอนสร้าง/แก้ไขเอกสาร
class courseOpeningRequest(BaseModel):
    degreeLevel: degreeLevelType  # ระดับการศึกษา
    requestScope: requestScopeType  # ขอบเขตการขอเปิดรายวิชา
    status: requestStatusType = "draft"  # สถานะเอกสาร
    confirmStatus: confirmStatusType = "notConfirm"  # สถานะการยืนยัน/อนุมัติ
    documentData: courseOpeningDocumentData  # ข้อมูลทั้งหมดของฟอร์ม


class courseOpeningRequestCreate(courseOpeningRequest):
    pass


# โครงข้อมูลตอนตอบกลับจากระบบ พร้อมข้อมูลสรุปและวันเวลาที่บันทึก
class courseOpeningRequestResponse(BaseModel):
    id: int  # รหัสเอกสาร
    degreeLevel: degreeLevelType  # ระดับการศึกษา
    requestScope: requestScopeType  # ขอบเขตการขอเปิดรายวิชา
    status: requestStatusType  # สถานะเอกสาร
    confirmStatus: confirmStatusType  # สถานะการยืนยัน/อนุมัติ
    documentData: courseOpeningDocumentData  # ข้อมูลทั้งหมดของฟอร์ม
    semester: str  # ภาคการศึกษาที่สรุปจาก generalForm
    academicYear: str  # ปีการศึกษาที่สรุปจาก generalForm
    curriculumName: str  # ชื่อหลักสูตรที่สรุปจาก generalForm
    majorName: str  # ชื่อสาขาที่สรุปจาก generalForm
    createdAt: datetime  # วันเวลาที่สร้างเอกสาร
    updatedAt: datetime  # วันเวลาที่แก้ไขล่าสุด
