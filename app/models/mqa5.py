from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class mqa5section1(BaseModel):
    courseCode: str  # รหัสวิชา
    nameThai: str  # ชื่อรายวิชาภาษาไทย
    nameEng: str  # ชื่อรายวิชาภาษาอังกฤษ


class mqa5section2(BaseModel):
    credits: int  # จำนวนหน่วยกิต
    creditsDetail: str  # รายละเอียดหน่วยกิต เช่น 3(3-0-6)

class mqa5section3(BaseModel):
    curriculum: List[str]  # หลักสูตร/สาขาวิชา/ประเภทของรายวิชา


class mqa5section4(BaseModel):
    teachers: List[str]  # รายชื่ออาจารย์ผู้สอน/ผู้รับผิดชอบรายวิชา


class mqa5section5(BaseModel):
    semester: int  # ภาคการศึกษา
    year: int  # ปีการศึกษา
    yearLevel: int  # ชั้นปี
    group: int  # กลุ่มเรียน
    studentCount: int  # จำนวนนักศึกษา


class mqa5section6(BaseModel):
    location: str  # สถานที่เรียน


class mqa5section7(BaseModel):
    pre: Optional[str]   # รายวิชาที่ต้องเรียนมาก่อน
    co: Optional[str]   # รายวิชาที่ต้องเรียนพร้อมกัน


class mqa5section8(BaseModel):
    updatedDate: date  # วันที่จัดทำหรือปรับปรุงผลการดำเนินการของรายวิชาครั้งล่าสุด


class mqa5section9(BaseModel):
    deviatedHours: Optional[str]   # รายงานชั่วโมงการสอนจริงที่คลาดเคลื่อนจากแผนการสอน


class mqa5section10(BaseModel):
    uncoveredTopics: Optional[str]   # หัวข้อที่สอนไม่ครอบคลุมตามแผน


class mqa5section11Row(BaseModel):
    clo: str  # ผลลัพธการเรียนรูที่คาดหวัง ของรายวิชา(CLOs)
    learning: str # ผลการเรียนรู้
    teaching: List[str]  # กลยุทธ์การสอน/วิธีการจัดการเรียนรู้ที่ได้ดำเนินการ
    evaluation: List[str]  # วิธีการประเมินผลที่ได้ดำเนินการ
    result: List[str]  # ผลที่เกิดกับนักศึกษา
    improve: List[str]  # แนวทางการพัฒนาปรับปรุง เพื่อให้นักศึกษาบรรลุตามแตละ CLO


class mqa5section11(BaseModel):
    rows: List[mqa5section11Row]  # รายการข้อมูลแต่ละแถวของข้อ 11


class GradeRow(BaseModel):
    grade: str  # ระดับคะแนน
    range: str  # ช่วงระดับคะแนน
    count: int  # จำนวนคน
    percent: float  # ร้อยละ

class Tolerance(BaseModel):
    deviation: Optional[str]   # ความคลาดเคลื่อนจากแผนการประเมิน
    reason: Optional[str]   # เหตุผล


class mqa5section12(BaseModel):
    registered: int  # จำนวนนักศึกษาที่ลงทะเบียนเรียน
    remaining: int  # จำนวนนักศึกษาที่คงอยู่เมื่อสิ้นสุดภาคการศึกษา
    withdrawn: int  # จำนวนนักศึกษาที่ถอน (W)
    grades: List[GradeRow]  # การกระจายของระดับคะแนน
    abnormalFactor: Optional[str]   # ปัจจัยที่ทำให้ระดับคะแนนผิดปกติ
    tolerance : List[Tolerance] # ความคลาดเคลื่อนจากแผนการประเมิน/เหตุผล

class IssueRow(BaseModel):
    issue: str  # ปัญหาที่พบ
    impact: str  # ผลกระทบต่อการเรียนรู้


class mqa5section13(BaseModel):
    resourceIssues: List[IssueRow]  # ปัญหาด้านทรัพยากรประกอบการเรียนและสิ่งอำนวยความสะดวก
    adminIssues: List[IssueRow]  # ปัญหาด้านการบริหารและองค์กร


class FeedbackRow(BaseModel):
    criticism: str  # ข้อวิพากษ์สำคัญ
    response: str  # ความเห็นของอาจารย์ผู้สอนต่อข้อวิพากษ์


class mqa5section14(BaseModel):
    systemFeedback: List[FeedbackRow]  # ข้อวิพากษ์สำคัญจากผลการประเมินโดยนักศึกษา
    otherFeedback: List[FeedbackRow]  # ข้อวิพากษ์สำคัญจากผลการประเมินโดยวิธีอื่น


class PastPlanRow(BaseModel):
    plan: Optional[str]  # แผนการปรับปรุงที่เสนอในภาคการศึกษาหรือปีการศึกษาที่ผ่านมา
    result: Optional[str]  # ผลการดำเนินการ


class NextPlanRow(BaseModel):
    plan: str  # ข้อเสนอ
    deadline: str  # กำหนดเวลาแล้วเสร็จ
    owner: str  # ผู้รับผิดชอบ


class mqa5section15(BaseModel):
    pastPlans: List[PastPlanRow]  # แผนการปรับปรุงที่เสนอในภาคการศึกษาหรือปีการศึกษาที่ผ่านมา และผลการดำเนินการ
    otherActions: List[str]  # ข้อเสนอแผนการปรับปรุงส าหรับภาคการศึกษา/ปีการศึกษาต่อไปที่มีความสอดคล้องกับผลลัพธ์การเรียนรู้ (PLO) ของหลักสูตร
    recommendations: List[str]  # ข้อเสนอแนะของอาจารย์ผู้รับผิดชอบรายวิชาต่ออาจารย์ผู้รับผิดชอบหลักสูตร
    nextPlans: List[NextPlanRow]  # ข้อเสนอแผนการปรับปรุงสำหรับภาคการศึกษาหรือปีการศึกษาต่อไป

class teacherSignRow(BaseModel):
    name: str  # ชื่ออาจารย์
    reportDate: date  # วันที่รายงาน
    signature: str   # ลายเซ็น 

class mqa5section16(BaseModel):
    integrations: List[str]  # รายการแผนการบูรณาการระหว่างรายวิชา
    subjectTeachers: List[teacherSignRow]  # รายชื่ออาจารย์ผู้รับผิดชอบรายวิชา
    curriculumTeachers: List[teacherSignRow]  # รายชื่ออาจารย์ผู้รับผิดชอบหลักสูตร


class MQA5(BaseModel):
    section1: mqa5section1
    section2: mqa5section2
    section3: mqa5section3
    section4: mqa5section4
    section5: mqa5section5
    section6: mqa5section6
    section7: mqa5section7
    section8: mqa5section8
    section9: mqa5section9
    section10: mqa5section10
    section11: mqa5section11
    section12: mqa5section12
    section13: mqa5section13
    section14: mqa5section14
    section15: mqa5section15
    section16: mqa5section16