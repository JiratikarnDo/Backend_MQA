from datetime import date as DateType, datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict

TQF5_EXAMPLE = {
    "course_id": 1,
    "section1": {
        "courseCode": "05-000-301",
        "nameThai": "ระบบฐานข้อมูล",
        "nameEng": "Database Systems"
    },
    "section2": {
        "credits": 3,
        "creditsDetail": "3(2-2-5)"
    },
    "section3": {
        "curriculum": ["บริหารธุรกิจบัณฑิต สาขาวิชาระบบสารสนเทศ"],
        "courseCategory": "วิชาเฉพาะด้าน"
    },
    "section4": {
        "teachers": ["อ.สมชาย สายคอม", "อ.สมหญิง รักเรียน"]
    },
    "section5": {
        "semester": 1,
        "year": 2569,
        "yearLevel": 2,
        "group": 1,
        "studentCount": 45
    },
    "section6": {
        "location": "อาคารคณะบริหารธุรกิจ มทร.ตะวันออก"
    },
    "section7": {
        "pre": "ไม่มี",
        "co": "ไม่มี"
    },
    "section8": {
        "updatedDate": "2026-05-12"
    },
    "section9": {
        "deviatedHours": "ไม่มี"
    },
    "section10": {
        "uncoveredTopics": "ไม่มี"
    },
    "section11": {
        "rows": [
            {
                "clo": "CLO1",
                "teach": "บรรยายและฝึกปฏิบัติ",
                "assess": "แบบฝึกหัดและสอบกลางภาค",
                "outcome": "นักศึกษาส่วนใหญ่เข้าใจหลักการฐานข้อมูล",
                "improve": "เพิ่มแบบฝึกหัดเรื่อง normalization"
            }
        ]
    },
    "section12": {
        "registered": 45,
        "remaining": 43,
        "withdrawn": 2,
        "grades": [
            {
                "grade": "A",
                "range": "80-100",
                "count": 8,
                "percent": 18.60
            },
            {
                "grade": "B+",
                "range": "75-79",
                "count": 10,
                "percent": 23.26
            }
        ],
        "abnormalFactor": "ไม่มี",
        "tolerance": [
            {
                "deviation": "ไม่มี",
                "reason": "ไม่มี"
            }
        ]
    },
    "section13": {
        "resourceIssues": [
            {
                "issue": "เครื่องคอมพิวเตอร์บางเครื่องช้า",
                "impact": "ทำให้การฝึกปฏิบัติบางช่วงล่าช้า"
            }
        ],
        "adminIssues": [
            {
                "issue": "ไม่มี",
                "impact": "ไม่มี"
            }
        ]
    },
    "section14": {
        "systemFeedback": [
            {
                "criticism": "ควรเพิ่มเวลาในหัวข้อ SQL",
                "response": "ปรับแผนการสอนในปีถัดไป"
            }
        ],
        "otherFeedback": [
            {
                "criticism": "ไม่มี",
                "response": "ไม่มี"
            }
        ]
    },
    "section15": {
        "pastPlans": [
            {
                "plan": "เพิ่มกิจกรรมฝึกปฏิบัติ",
                "result": "นักศึกษาทำแบบฝึกหัดได้ดีขึ้น"
            }
        ],
        "otherActions": ["จัดทำเอกสารประกอบเพิ่มเติม"],
        "recommendations": ["ควรเพิ่มเวลา lab"],
        "nextPlans": [
            {
                "plan": "ปรับเนื้อหา normalization",
                "deadline": "ก่อนเปิดภาคเรียนถัดไป",
                "owner": "อ.สมชาย สายคอม"
            }
        ]
    },
    "section16": {
        "integrations": ["บูรณาการกับรายวิชาการพัฒนาเว็บแอปพลิเคชัน"],
        "subjectTeachers": [
            {
                "name": "อ.สมชาย สายคอม",
                "signature": "สมชาย",
                "date": "2026-05-12"
            }
        ],
        "curriculumTeachers": [
            {
                "name": "อ.สมหญิง รักเรียน",
                "signature": "สมหญิง",
                "date": "2026-05-12"
            }
        ]
    }
}

class Section1Base(BaseModel):
    courseCode: Optional[str] = None
    nameThai: Optional[str] = None
    nameEng: Optional[str] = None

class Section2Base(BaseModel):
    credits: Optional[int] = None
    creditsDetail: Optional[str] = None

class Section3Base(BaseModel):
    curriculum: Optional[List[str]] = []
    courseCategory: Optional[str] = None

class Section4Base(BaseModel):
    teachers: Optional[List[str]] = []

class Section5Base(BaseModel):
    semester: Optional[int] = None
    year: Optional[int] = None
    yearLevel: Optional[int] = None
    group: Optional[int] = None
    studentCount: Optional[int] = None

class Section6Base(BaseModel):
    location: Optional[str] = None

class Section7Base(BaseModel):
    pre: Optional[str] = None
    co: Optional[str] = None

class Section8Base(BaseModel):
    updatedDate: Optional[DateType] = None

class Section9Base(BaseModel):
    deviatedHours: Optional[str] = None

class Section10Base(BaseModel):
    uncoveredTopics: Optional[str] = None

class Section11RowBase(BaseModel):
    clo: Optional[str] = None
    teach: Optional[str] = None
    assess: Optional[str] = None
    outcome: Optional[str] = None
    improve: Optional[str] = None

class Section11Base(BaseModel):
    rows: Optional[List[Section11RowBase]] = []

class GradeRowBase(BaseModel):
    grade: Optional[str] = None
    range: Optional[str] = None
    count: Optional[int] = None
    percent: Optional[float] = None

class ToleranceBase(BaseModel):
    deviation: Optional[str] = None
    reason: Optional[str] = None

class Section12Base(BaseModel):
    registered: Optional[int] = None
    remaining: Optional[int] = None
    withdrawn: Optional[int] = None
    grades: Optional[List[GradeRowBase]] = []
    abnormalFactor: Optional[str] = None
    tolerance: Optional[List[ToleranceBase]] = None

class IssueRowBase(BaseModel):
    issue: Optional[str] = None
    impact: Optional[str] = None

class Section13Base(BaseModel):
    resourceIssues: Optional[List[IssueRowBase]] = []
    adminIssues: Optional[List[IssueRowBase]] = []

class FeedbackRowBase(BaseModel):
    criticism: Optional[str] = None
    response: Optional[str] = None

class Section14Base(BaseModel):
    systemFeedback: Optional[List[FeedbackRowBase]] = []
    otherFeedback: Optional[List[FeedbackRowBase]] = []

class PastPlanRowBase(BaseModel):
    plan: Optional[str] = None
    result: Optional[str] = None

class NextPlanRowBase(BaseModel):
    plan: Optional[str] = None
    deadline: Optional[str] = None
    owner: Optional[str] = None

class Section15Base(BaseModel):
    pastPlans: Optional[List[PastPlanRowBase]] = []
    otherActions: Optional[List[str]] = []
    recommendations: Optional[List[str]] = []
    nextPlans: Optional[List[NextPlanRowBase]] = []

class TeacherSignRowBase(BaseModel):
    name: Optional[str] = None
    signature: Optional[str] = None
    date: Optional[DateType] = None

class Section16Base(BaseModel):
    integrations: Optional[List[str]] = []
    subjectTeachers: Optional[List[TeacherSignRowBase]] = []
    curriculumTeachers: Optional[List[TeacherSignRowBase]] = []

class TQF5Create(BaseModel):
    course_id: Optional[int] = None
    section1: Section1Base
    section2: Section2Base
    section3: Section3Base
    section4: Section4Base
    section5: Section5Base
    section6: Section6Base
    section7: Section7Base
    section8: Section8Base
    section9: Section9Base
    section10: Section10Base
    section11: Section11Base
    section12: Section12Base
    section13: Section13Base
    section14: Section14Base
    section15: Section15Base
    section16: Section16Base

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra='forbid'
    )

class TQF5TeacherResponse(BaseModel):
    id: int
    name: Optional[str] = None
    model_config = {"from_attributes": True}

class TQF5CLOResultResponse(BaseModel):
    id: int
    clo: Optional[str] = None
    teach: Optional[str] = None
    assess: Optional[str] = None
    outcome: Optional[str] = None
    improve: Optional[str] = None
    model_config = {"from_attributes": True}

class TQF5GradeResponse(BaseModel):
    id: int
    grade: Optional[str] = None
    range: Optional[str] = None
    count: Optional[int] = None
    percent: Optional[float] = None
    model_config = {"from_attributes": True}

class TQF5ToleranceResponse(BaseModel):
    id: int
    deviation: Optional[str] = None
    reason: Optional[str] = None
    model_config = {"from_attributes": True}

class TQF5IssueResponse(BaseModel):
    id: int
    issue_type: Optional[str] = None
    issue: Optional[str] = None
    impact: Optional[str] = None
    model_config = {"from_attributes": True}

class TQF5FeedbackResponse(BaseModel):
    id: int
    feedback_type: Optional[str] = None
    criticism: Optional[str] = None
    response: Optional[str] = None
    model_config = {"from_attributes": True}

class TQF5PastPlanResponse(BaseModel):
    id: int
    plan: Optional[str] = None
    result: Optional[str] = None
    model_config = {"from_attributes": True}

class TQF5NextPlanResponse(BaseModel):
    id: int
    plan: Optional[str] = None
    deadline: Optional[str] = None
    owner: Optional[str] = None
    model_config = {"from_attributes": True}

class TQF5ListItemResponse(BaseModel):
    id: int
    item_type: Optional[str] = None
    detail: Optional[str] = None
    model_config = {"from_attributes": True}

class TQF5SignerResponse(BaseModel):
    id: int
    signer_type: Optional[str] = None
    name: Optional[str] = None
    signature: Optional[str] = None
    signed_date: Optional[DateType] = None
    model_config = {"from_attributes": True}

class TQF5Response(BaseModel):
    id: int
    course_id: Optional[int] = None
    status: str
    creator_id: Optional[int] = None
    department_id: Optional[int] = None
    documentData: Dict[str, Any]
    courseCode: Optional[str] = None
    nameThai: Optional[str] = None
    nameEng: Optional[str] = None
    credits: Optional[int] = None
    creditsDetail: Optional[str] = None
    curriculum: Optional[Any] = None
    courseCategory: Optional[str] = None
    teachers: Optional[Any] = None
    semester: Optional[int] = None
    year: Optional[int] = None
    yearLevel: Optional[int] = None
    groupNumber: Optional[int] = None
    studentCount: Optional[int] = None
    location: Optional[str] = None
    pre: Optional[str] = None
    co: Optional[str] = None
    updatedDate: Optional[DateType] = None
    deviatedHours: Optional[str] = None
    uncoveredTopics: Optional[str] = None
    registered: Optional[int] = None
    remaining: Optional[int] = None
    withdrawn: Optional[int] = None
    abnormalFactor: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    teachers_list: Optional[List[TQF5TeacherResponse]] = []
    clo_results: Optional[List[TQF5CLOResultResponse]] = []
    grades: Optional[List[TQF5GradeResponse]] = []
    tolerances: Optional[List[TQF5ToleranceResponse]] = []
    issues: Optional[List[TQF5IssueResponse]] = []
    feedbacks: Optional[List[TQF5FeedbackResponse]] = []
    past_plans: Optional[List[TQF5PastPlanResponse]] = []
    next_plans: Optional[List[TQF5NextPlanResponse]] = []
    list_items: Optional[List[TQF5ListItemResponse]] = []
    signers: Optional[List[TQF5SignerResponse]] = []

    model_config = {"from_attributes": True}