from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class mqa3section1(BaseModel):
    courseCode: str  # รหัสวิชา
    courseNameThai: str  # ชื่อรายวิชาภาษาไทย
    courseNameEnglish: str  # ชื่อรายวิชาภาษาอังกฤษ


class mqa3section2(BaseModel):
    credits: int  # จำนวนหน่วยกิต
    creditsDetail: str  # รายละเอียดหน่วยกิต เช่น 3(3-0-6)


class mqa3section3(BaseModel):
    curriculum: str  # หลักสูตร/สาขาวิชา
    subjectType: str  # ประเภทของรายวิชา


class mqa3section4(BaseModel):
    teacherNames: List[str]  # รายชื่ออาจารย์ผู้สอน/ผู้รับผิดชอบรายวิชา


class mqa3section5(BaseModel):
    semester: int  # ภาคการศึกษา
    schoolYear: int  # ปีการศึกษา
    yearLevel: int  # ชั้นปี
    group: int  # กลุ่มเรียน
    studentCount: int  # จำนวนนักศึกษา


class mqa3section6(BaseModel):
    location: str  # สถานที่เรียน


class mqa3section7(BaseModel):
    preSubject: Optional[str]   # รายวิชาที่ต้องเรียนมาก่อน
    coSubject: Optional[str]   # รายวิชาที่ต้องเรียนพร้อมกัน


class mqa3section8(BaseModel):
    lastUpdatedDate: date  # วันที่จัดทำหรือปรับปรุงรายละเอียดรายวิชาครั้งล่าสุด


class mqa3section9(BaseModel):
    subjectDescription: str  # คำอธิบายรายวิชา


class mqa3section10(BaseModel):
    subjectObjectives: List[str]  # วัตถุประสงค์ในการพัฒนา/ปรับปรุงรายวิชา


class mqa3section11(BaseModel):
    plos: List[str]  # ผลลัพธ์การเรียนรู้ของหลักสูตร (PLOs)


class mqa3section12(BaseModel):
    clos: List[str]  # ผลลัพธ์การเรียนรู้ที่คาดหวังของรายวิชา (CLOs)


class mqa3section13(BaseModel):
    lectureHours: str  # ชั่วโมงบรรยายต่อสัปดาห์
    practiceHours: str  # ชั่วโมงฝึกปฏิบัติ/ภาคสนาม/ฝึกงานต่อสัปดาห์
    selfStudyHours: str  # ชั่วโมงศึกษาด้วยตนเองต่อสัปดาห์
    contact: str  # แนวทางและช่องทางการติดต่อกับนักศึกษา


class mqa3section14Row(BaseModel):
    clo: str  # CLO ของแถวนั้น
    learning: str 
    teaching: List[str]  # กลยุทธ์การสอนตาม CLO
    evaluation: List[str]  # กลยุทธ์สำหรับวิธีการวัดและประเมินผลตาม CLO


class mqa3section14(BaseModel):
    rows: List[mqa3section14Row]  # รายการข้อมูลแต่ละแถวของตารางข้อ 14


class mqa3section15Row(BaseModel):
    week: int  # สัปดาห์ที่
    topic: str   # หัวข้อ/รายละเอียด
    clo: List[str]  # CLOs ที่เกี่ยวข้อง
    hours: int  # จำนวนชั่วโมง
    activity: str # กิจกรรมการเรียนการสอน/สื่อที่ใช้
    teacher: str # ผู้สอน


class mqa3section15(BaseModel):
    rows: List[mqa3section15Row]  # รายการข้อมูลแต่ละแถวของแผนการสอน


class mqa3section16Row(BaseModel):
    clo: str  # CLO ของแถวนั้น
    learning: str # ผลการเรียนรู้
    assessmentActivities: List[str]  # กิจกรรมการประเมินผลการเรียนรู้ของผู้เรียน
    assessmentWeeks: str  # กำหนดการประเมิน (สัปดาห์ที่)
    scorePercent: List[int]  # สัดส่วนของการประเมินผลเป็นเปอร์เซ็นต์


class mqa3section16(BaseModel):
    rows: List[mqa3section16Row]  # รายการข้อมูลแต่ละแถวของแผนการประเมิน


class mqa3section17(BaseModel):
    agreements: List[str]  # ข้อตกลงร่วมกันระหว่างผู้เรียนและผู้สอน


class mqa3section18(BaseModel):
    courseIntegration: List[str]  # แผนการบูรณาการระหว่างรายวิชา


class mqa3section19(BaseModel):
    textbooks: List[str]  # หนังสือและเอกสารประกอบการสอน
    onlineSources: List[str]  # เว็บไซต์และแหล่งข้อมูลออนไลน์


class MQA3(BaseModel):
    section1: mqa3section1  
    section2: mqa3section2  
    section3: mqa3section3  
    section4: mqa3section4  
    section5: mqa3section5  
    section6: mqa3section6  
    section7: mqa3section7  
    section8: mqa3section8  
    section9: mqa3section9  
    section10: mqa3section10  
    section11: mqa3section11  
    section12: mqa3section12  
    section13: mqa3section13  
    section14: mqa3section14  
    section15: mqa3section15  
    section16: mqa3section16  
    section17: mqa3section17  
    section18: mqa3section18  
    section19: mqa3section19  