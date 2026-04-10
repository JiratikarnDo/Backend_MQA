# -- Section 1: ข้อมูลรายวิชา
# CREATE TABLE mqa5_section1 (
#     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
#     course_code VARCHAR(20) NOT NULL,
#     name_thai VARCHAR(255) NOT NULL,
#     name_eng VARCHAR(255) NOT NULL
# );

# -- Section 2: หน่วยกิต
# CREATE TABLE mqa5_section2 (
#     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
#     course_id UUID NOT NULL REFERENCES mqa5_section1(id) ON DELETE CASCADE,
#     credits INT NOT NULL,
#     credits_detail VARCHAR(50)
# );

# -- Section 3: หลักสูตร/สาขาวิชา
# CREATE TABLE mqa5_section3 (
#     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
#     course_id UUID NOT NULL REFERENCES mqa5_section1(id) ON DELETE CASCADE,
#     curriculum VARCHAR(255) NOT NULL
# );

# -- Section 4: อาจารย์ผู้สอน
# CREATE TABLE mqa5_section4 (
#     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
#     course_id UUID NOT NULL REFERENCES mqa5_section1(id) ON DELETE CASCADE,
#     teacher_name VARCHAR(255) NOT NULL
# );

# -- Section 5: ภาค/ปี/กลุ่ม/จำนวนนักศึกษา
# CREATE TABLE mqa5_section5 (
#     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
#     course_id UUID NOT NULL REFERENCES mqa5_section1(id) ON DELETE CASCADE,
#     semester INT NOT NULL,
#     year INT NOT NULL,
#     year_level INT NOT NULL,
#     group_no INT NOT NULL,
#     student_count INT NOT NULL
# );

# -- Section 6: สถานที่เรียน
# CREATE TABLE mqa5_section6 (
#     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
#     course_id UUID NOT NULL REFERENCES mqa5_section1(id) ON DELETE CASCADE,
#     location VARCHAR(255) NOT NULL
# );

# -- Section 7: วิชาบังคับก่อน/ร่วม
# CREATE TABLE mqa5_section7 (
#     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
#     course_id UUID NOT NULL REFERENCES mqa5_section1(id) ON DELETE CASCADE,
#     pre_requisite TEXT,
#     co_requisite TEXT
# );

# -- Section 8: วันที่จัดทำ/ปรับปรุง
# CREATE TABLE mqa5_section8 (
#     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
#     course_id UUID NOT NULL REFERENCES mqa5_section1(id) ON DELETE CASCADE,
#     updated_date DATE NOT NULL
# );

# -- Section 9: ชั่วโมงสอนที่คลาดเคลื่อน
# CREATE TABLE mqa5_section9 (
#     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
#     course_id UUID NOT NULL REFERENCES mqa5_section1(id) ON DELETE CASCADE,
#     deviated_hours TEXT
# );

# -- Section 10: หัวข้อที่สอนไม่ครอบคลุม
# CREATE TABLE mqa5_section10 (
#     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
#     course_id UUID NOT NULL REFERENCES mqa5_section1(id) ON DELETE CASCADE,
#     uncovered_topics TEXT
# );

# -- Section 11: CLO แต่ละข้อ
# CREATE TABLE mqa5_section11 (
#     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
#     course_id UUID NOT NULL REFERENCES mqa5_section1(id) ON DELETE CASCADE,
#     sort_order INT DEFAULT 0,
#     clo TEXT NOT NULL,
#     learning TEXT,
#     teaching TEXT[],
#     evaluation TEXT[],
#     result TEXT[],
#     improve TEXT[]
# );

# -- Section 12: สถิติการลงทะเบียนและคะแนน
# CREATE TABLE mqa5_section12 (
#     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
#     course_id UUID NOT NULL REFERENCES mqa5_section1(id) ON DELETE CASCADE,
#     registered INT NOT NULL,
#     remaining INT NOT NULL,
#     withdrawn INT NOT NULL,
#     abnormal_factor TEXT
# );

# CREATE TABLE mqa5_section12_grades (
#     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
#     section12_id UUID NOT NULL REFERENCES mqa5_section12(id) ON DELETE CASCADE,
#     grade VARCHAR(5) NOT NULL,
#     grade_range VARCHAR(50),
#     count INT NOT NULL,
#     percent NUMERIC(5,2) NOT NULL
# );

# CREATE TABLE mqa5_section12_tolerance (
#     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
#     section12_id UUID NOT NULL REFERENCES mqa5_section12(id) ON DELETE CASCADE,
#     deviation TEXT,
#     reason TEXT
# );

# -- Section 13: ปัญหาด้านทรัพยากรและการบริหาร
# CREATE TABLE mqa5_section13 (
#     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
#     course_id UUID NOT NULL REFERENCES mqa5_section1(id) ON DELETE CASCADE,
#     issue_type VARCHAR(20) NOT NULL CHECK (issue_type IN ('resource', 'admin')),
#     issue TEXT NOT NULL,
#     impact TEXT
# );

# -- Section 14: Feedback จากนักศึกษาและวิธีอื่น
# CREATE TABLE mqa5_section14 (
#     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
#     course_id UUID NOT NULL REFERENCES mqa5_section1(id) ON DELETE CASCADE,
#     feedback_type VARCHAR(20) NOT NULL CHECK (feedback_type IN ('system', 'other')),
#     criticism TEXT NOT NULL,
#     response TEXT
# );

# -- Section 15: แผนปรับปรุงที่ผ่านมา + ถัดไป
# CREATE TABLE mqa5_section15 (
#     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
#     course_id UUID NOT NULL REFERENCES mqa5_section1(id) ON DELETE CASCADE,
#     other_actions TEXT[],
#     recommendations TEXT[]
# );

# CREATE TABLE mqa5_section15_past (
#     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
#     section15_id UUID NOT NULL REFERENCES mqa5_section15(id) ON DELETE CASCADE,
#     plan TEXT,
#     result TEXT
# );

# CREATE TABLE mqa5_section15_next (
#     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
#     section15_id UUID NOT NULL REFERENCES mqa5_section15(id) ON DELETE CASCADE,
#     plan TEXT NOT NULL,
#     deadline VARCHAR(100),
#     owner VARCHAR(255)
# );

# -- Section 16: บูรณาการและลายเซ็น
# CREATE TABLE mqa5_section16 (
#     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
#     course_id UUID NOT NULL REFERENCES mqa5_section1(id) ON DELETE CASCADE
# );

# CREATE TABLE mqa5_section16_integration (
#     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
#     section16_id UUID NOT NULL REFERENCES mqa5_section16(id) ON DELETE CASCADE,
#     description TEXT NOT NULL
# );

# CREATE TABLE mqa5_section16_signature (
#     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
#     section16_id UUID NOT NULL REFERENCES mqa5_section16(id) ON DELETE CASCADE,
#     signer_type VARCHAR(30) NOT NULL CHECK (signer_type IN ('subject_teacher', 'curriculum_teacher')),
#     name VARCHAR(255) NOT NULL,
#     report_date DATE,
#     signature TEXT
# );