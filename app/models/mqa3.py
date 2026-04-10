from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey
from sqlalchemy.sql import func
from app.Interface.sql_db import base

# ===========================
# MAIN TABLE
# ===========================
class MQA3(base):
    __tablename__ = "mqa3"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# ===========================
# SECTION 1: Course Info
# ===========================
class MQA3Section1(base):
    __tablename__ = "mqa3_section1"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    mqa3_id = Column(Integer, ForeignKey("mqa3.id", ondelete="CASCADE"), nullable=False)
    course_code = Column(String(50), nullable=False)
    course_name_thai = Column(String(255), nullable=False)
    course_name_english = Column(String(255), nullable=False)

# ===========================
# SECTION 2: Credits
# ===========================
class MQA3Section2(base):
    __tablename__ = "mqa3_section2"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    mqa3_id = Column(Integer, ForeignKey("mqa3.id", ondelete="CASCADE"), nullable=False)
    credits = Column(Integer, nullable=False)
    credits_detail = Column(String(255), nullable=False)

# ===========================
# SECTION 3: Curriculum
# ===========================
class MQA3Section3(base):
    __tablename__ = "mqa3_section3"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    mqa3_id = Column(Integer, ForeignKey("mqa3.id", ondelete="CASCADE"), nullable=False)
    curriculum = Column(String(255), nullable=False)
    subject_type = Column(String(100), nullable=False)

# ===========================
# SECTION 4: Teachers
# ===========================
class MQA3Section4(base):
    __tablename__ = "mqa3_section4"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    mqa3_id = Column(Integer, ForeignKey("mqa3.id", ondelete="CASCADE"), nullable=False)

class MQA3Section4TeacherNames(base):
    __tablename__ = "mqa3_section4_teacher_names"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    section4_id = Column(Integer, ForeignKey("mqa3_section4.id", ondelete="CASCADE"), nullable=False)
    teacher_name = Column(String(255), nullable=False)

# ===========================
# SECTION 5: Semester Info
# ===========================
class MQA3Section5(base):
    __tablename__ = "mqa3_section5"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    mqa3_id = Column(Integer, ForeignKey("mqa3.id", ondelete="CASCADE"), nullable=False)
    semester = Column(Integer, nullable=False)
    school_year = Column(Integer, nullable=False)
    year_level = Column(Integer, nullable=False)
    group = Column(Integer, nullable=False)  # หมายเหตุ: group เป็นคำสงวนในบาง DB แต่ SQLAlchemy จะจัดการให้ตอนสร้างครับ
    student_count = Column(Integer, nullable=False)

# ===========================
# SECTION 6: Location
# ===========================
class MQA3Section6(base):
    __tablename__ = "mqa3_section6"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    mqa3_id = Column(Integer, ForeignKey("mqa3.id", ondelete="CASCADE"), nullable=False)
    location = Column(String(255), nullable=False)

# ===========================
# SECTION 7: Pre/Co Subject
# ===========================
class MQA3Section7(base):
    __tablename__ = "mqa3_section7"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    mqa3_id = Column(Integer, ForeignKey("mqa3.id", ondelete="CASCADE"), nullable=False)
    pre_subject = Column(String(255), nullable=True)
    co_subject = Column(String(255), nullable=True)

# ===========================
# SECTION 8: Last Updated
# ===========================
class MQA3Section8(base):
    __tablename__ = "mqa3_section8"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    mqa3_id = Column(Integer, ForeignKey("mqa3.id", ondelete="CASCADE"), nullable=False)
    last_updated_date = Column(Date, nullable=False)

# ===========================
# SECTION 9: Description
# ===========================
class MQA3Section9(base):
    __tablename__ = "mqa3_section9"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    mqa3_id = Column(Integer, ForeignKey("mqa3.id", ondelete="CASCADE"), nullable=False)
    subject_description = Column(Text, nullable=False)

# ===========================
# SECTION 10: Objectives
# ===========================
class MQA3Section10(base):
    __tablename__ = "mqa3_section10"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    mqa3_id = Column(Integer, ForeignKey("mqa3.id", ondelete="CASCADE"), nullable=False)

class MQA3Section10Objectives(base):
    __tablename__ = "mqa3_section10_objectives"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    section10_id = Column(Integer, ForeignKey("mqa3_section10.id", ondelete="CASCADE"), nullable=False)
    objective = Column(Text, nullable=False)

# ===========================
# SECTION 11: PLOs
# ===========================
class MQA3Section11(base):
    __tablename__ = "mqa3_section11"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    mqa3_id = Column(Integer, ForeignKey("mqa3.id", ondelete="CASCADE"), nullable=False)

class MQA3Section11PLOs(base):
    __tablename__ = "mqa3_section11_plos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    section11_id = Column(Integer, ForeignKey("mqa3_section11.id", ondelete="CASCADE"), nullable=False)
    plo = Column(Text, nullable=False)

# ===========================
# SECTION 12: CLOs
# ===========================
class MQA3Section12(base):
    __tablename__ = "mqa3_section12"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    mqa3_id = Column(Integer, ForeignKey("mqa3.id", ondelete="CASCADE"), nullable=False)

class MQA3Section12CLOs(base):
    __tablename__ = "mqa3_section12_clos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    section12_id = Column(Integer, ForeignKey("mqa3_section12.id", ondelete="CASCADE"), nullable=False)
    clo = Column(Text, nullable=False)

# ===========================
# SECTION 13: Hours
# ===========================
class MQA3Section13(base):
    __tablename__ = "mqa3_section13"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    mqa3_id = Column(Integer, ForeignKey("mqa3.id", ondelete="CASCADE"), nullable=False)
    lecture_hours = Column(String(50), nullable=False)
    practice_hours = Column(String(50), nullable=False)
    self_study_hours = Column(String(50), nullable=False)
    contact = Column(String(255), nullable=False)

# ===========================
# SECTION 14: CLO-Learning Map
# ===========================
class MQA3Section14(base):
    __tablename__ = "mqa3_section14"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    mqa3_id = Column(Integer, ForeignKey("mqa3.id", ondelete="CASCADE"), nullable=False)

class MQA3Section14Rows(base):
    __tablename__ = "mqa3_section14_rows"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    section14_id = Column(Integer, ForeignKey("mqa3_section14.id", ondelete="CASCADE"), nullable=False)
    clo = Column(String(100), nullable=False)
    learning = Column(Text, nullable=False)

class MQA3Section14RowTeaching(base):
    __tablename__ = "mqa3_section14_row_teaching"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    section14_row_id = Column(Integer, ForeignKey("mqa3_section14_rows.id", ondelete="CASCADE"), nullable=False)
    teaching = Column(Text, nullable=False)

class MQA3Section14RowEvaluation(base):
    __tablename__ = "mqa3_section14_row_evaluation"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    section14_row_id = Column(Integer, ForeignKey("mqa3_section14_rows.id", ondelete="CASCADE"), nullable=False)
    evaluation = Column(Text, nullable=False)

# ===========================
# SECTION 15: Weekly Schedule
# ===========================
class MQA3Section15(base):
    __tablename__ = "mqa3_section15"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    mqa3_id = Column(Integer, ForeignKey("mqa3.id", ondelete="CASCADE"), nullable=False)

class MQA3Section15Rows(base):
    __tablename__ = "mqa3_section15_rows"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    section15_id = Column(Integer, ForeignKey("mqa3_section15.id", ondelete="CASCADE"), nullable=False)
    week = Column(Integer, nullable=False)
    topic = Column(Text, nullable=False)
    hours = Column(Integer, nullable=False)
    activity = Column(Text, nullable=False)
    teacher = Column(String(255), nullable=False)

class MQA3Section15RowCLOs(base):
    __tablename__ = "mqa3_section15_row_clos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    section15_row_id = Column(Integer, ForeignKey("mqa3_section15_rows.id", ondelete="CASCADE"), nullable=False)
    clo = Column(String(100), nullable=False)

# ===========================
# SECTION 16: Assessment
# ===========================
class MQA3Section16(base):
    __tablename__ = "mqa3_section16"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    mqa3_id = Column(Integer, ForeignKey("mqa3.id", ondelete="CASCADE"), nullable=False)

class MQA3Section16Rows(base):
    __tablename__ = "mqa3_section16_rows"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    section16_id = Column(Integer, ForeignKey("mqa3_section16.id", ondelete="CASCADE"), nullable=False)
    clo = Column(String(100), nullable=False)
    learning = Column(Text, nullable=False)
    assessment_weeks = Column(String(100), nullable=False)

class MQA3Section16RowActivities(base):
    __tablename__ = "mqa3_section16_row_activities"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    section16_row_id = Column(Integer, ForeignKey("mqa3_section16_rows.id", ondelete="CASCADE"), nullable=False)
    activity = Column(Text, nullable=False)

class MQA3Section16RowScorePercents(base):
    __tablename__ = "mqa3_section16_row_score_percents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    section16_row_id = Column(Integer, ForeignKey("mqa3_section16_rows.id", ondelete="CASCADE"), nullable=False)
    score_percent = Column(Integer, nullable=False)

# ===========================
# SECTION 17: Agreements
# ===========================
class MQA3Section17(base):
    __tablename__ = "mqa3_section17"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    mqa3_id = Column(Integer, ForeignKey("mqa3.id", ondelete="CASCADE"), nullable=False)

class MQA3Section17Agreements(base):
    __tablename__ = "mqa3_section17_agreements"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    section17_id = Column(Integer, ForeignKey("mqa3_section17.id", ondelete="CASCADE"), nullable=False)
    agreement = Column(Text, nullable=False)

# ===========================
# SECTION 18: Course Integration
# ===========================
class MQA3Section18(base):
    __tablename__ = "mqa3_section18"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    mqa3_id = Column(Integer, ForeignKey("mqa3.id", ondelete="CASCADE"), nullable=False)

class MQA3Section18Integrations(base):
    __tablename__ = "mqa3_section18_integrations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    section18_id = Column(Integer, ForeignKey("mqa3_section18.id", ondelete="CASCADE"), nullable=False)
    course_integration = Column(Text, nullable=False)

# ===========================
# SECTION 19: References
# ===========================
class MQA3Section19(base):
    __tablename__ = "mqa3_section19"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    mqa3_id = Column(Integer, ForeignKey("mqa3.id", ondelete="CASCADE"), nullable=False)

class MQA3Section19Textbooks(base):
    __tablename__ = "mqa3_section19_textbooks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    section19_id = Column(Integer, ForeignKey("mqa3_section19.id", ondelete="CASCADE"), nullable=False)
    textbook = Column(Text, nullable=False)

class MQA3Section19OnlineSources(base):
    __tablename__ = "mqa3_section19_online_sources"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    section19_id = Column(Integer, ForeignKey("mqa3_section19.id", ondelete="CASCADE"), nullable=False)
    online_source = Column(Text, nullable=False)