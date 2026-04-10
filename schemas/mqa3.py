# -- ===========================
# -- MAIN TABLE
# -- ===========================
# CREATE TABLE mqa3 (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

# -- ===========================
# -- SECTION 1: Course Info
# -- ===========================
# CREATE TABLE mqa3_section1 (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     mqa3_id INT NOT NULL,
#     course_code VARCHAR(50) NOT NULL,
#     course_name_thai VARCHAR(255) NOT NULL,
#     course_name_english VARCHAR(255) NOT NULL,
#     FOREIGN KEY (mqa3_id) REFERENCES mqa3(id) ON DELETE CASCADE
# );

# -- ===========================
# -- SECTION 2: Credits
# -- ===========================
# CREATE TABLE mqa3_section2 (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     mqa3_id INT NOT NULL,
#     credits INT NOT NULL,
#     credits_detail VARCHAR(255) NOT NULL,
#     FOREIGN KEY (mqa3_id) REFERENCES mqa3(id) ON DELETE CASCADE
# );

# -- ===========================
# -- SECTION 3: Curriculum
# -- ===========================
# CREATE TABLE mqa3_section3 (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     mqa3_id INT NOT NULL,
#     curriculum VARCHAR(255) NOT NULL,
#     subject_type VARCHAR(100) NOT NULL,
#     FOREIGN KEY (mqa3_id) REFERENCES mqa3(id) ON DELETE CASCADE
# );

# -- ===========================
# -- SECTION 4: Teachers (ยุบตารางกลางทิ้ง เชื่อม mqa3_id โดยตรง)
# -- ===========================
# CREATE TABLE mqa3_section4_teacher_names (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     mqa3_id INT NOT NULL,
#     teacher_name VARCHAR(255) NOT NULL,
#     FOREIGN KEY (mqa3_id) REFERENCES mqa3(id) ON DELETE CASCADE
# );

# -- ===========================
# -- SECTION 5: Semester Info
# -- ===========================
# CREATE TABLE mqa3_section5 (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     mqa3_id INT NOT NULL,
#     semester INT NOT NULL,
#     school_year INT NOT NULL,
#     year_level INT NOT NULL,
#     `group` INT NOT NULL, -- ใช้ backtick (`) ครอบ group เพราะเป็นคำสงวนใน MySQL
#     student_count INT NOT NULL,
#     FOREIGN KEY (mqa3_id) REFERENCES mqa3(id) ON DELETE CASCADE
# );

# -- ===========================
# -- SECTION 6: Location
# -- ===========================
# CREATE TABLE mqa3_section6 (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     mqa3_id INT NOT NULL,
#     location VARCHAR(255) NOT NULL,
#     FOREIGN KEY (mqa3_id) REFERENCES mqa3(id) ON DELETE CASCADE
# );

# -- ===========================
# -- SECTION 7: Pre/Co Subject
# -- ===========================
# CREATE TABLE mqa3_section7 (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     mqa3_id INT NOT NULL,
#     pre_subject VARCHAR(255),
#     co_subject VARCHAR(255),
#     FOREIGN KEY (mqa3_id) REFERENCES mqa3(id) ON DELETE CASCADE
# );

# -- ===========================
# -- SECTION 8: Last Updated
# -- ===========================
# CREATE TABLE mqa3_section8 (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     mqa3_id INT NOT NULL,
#     last_updated_date DATE NOT NULL,
#     FOREIGN KEY (mqa3_id) REFERENCES mqa3(id) ON DELETE CASCADE
# );

# -- ===========================
# -- SECTION 9: Description
# -- ===========================
# CREATE TABLE mqa3_section9 (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     mqa3_id INT NOT NULL,
#     subject_description TEXT NOT NULL,
#     FOREIGN KEY (mqa3_id) REFERENCES mqa3(id) ON DELETE CASCADE
# );

# -- ===========================
# -- SECTION 10: Objectives (ยุบตารางกลางทิ้ง)
# -- ===========================
# CREATE TABLE mqa3_section10_objectives (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     mqa3_id INT NOT NULL,
#     objective TEXT NOT NULL,
#     FOREIGN KEY (mqa3_id) REFERENCES mqa3(id) ON DELETE CASCADE
# );

# -- ===========================
# -- SECTION 11: PLOs (ยุบตารางกลางทิ้ง)
# -- ===========================
# CREATE TABLE mqa3_section11_plos (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     mqa3_id INT NOT NULL,
#     plo TEXT NOT NULL,
#     FOREIGN KEY (mqa3_id) REFERENCES mqa3(id) ON DELETE CASCADE
# );

# -- ===========================
# -- SECTION 12: CLOs (ยุบตารางกลางทิ้ง)
# -- ===========================
# CREATE TABLE mqa3_section12_clos (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     mqa3_id INT NOT NULL,
#     clo TEXT NOT NULL,
#     FOREIGN KEY (mqa3_id) REFERENCES mqa3(id) ON DELETE CASCADE
# );

# -- ===========================
# -- SECTION 13: Hours
# -- ===========================
# CREATE TABLE mqa3_section13 (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     mqa3_id INT NOT NULL,
#     lecture_hours VARCHAR(50) NOT NULL,
#     practice_hours VARCHAR(50) NOT NULL,
#     self_study_hours VARCHAR(50) NOT NULL,
#     contact VARCHAR(255) NOT NULL,
#     FOREIGN KEY (mqa3_id) REFERENCES mqa3(id) ON DELETE CASCADE
# );

# -- ===========================
# -- SECTION 14: CLO-Learning Map (ยุบตารางแรกสุดทิ้ง)
# -- ===========================
# CREATE TABLE mqa3_section14_rows (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     mqa3_id INT NOT NULL,
#     clo VARCHAR(100) NOT NULL,
#     learning TEXT NOT NULL,
#     FOREIGN KEY (mqa3_id) REFERENCES mqa3(id) ON DELETE CASCADE
# );

# CREATE TABLE mqa3_section14_row_teaching (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     section14_row_id INT NOT NULL,
#     teaching TEXT NOT NULL,
#     FOREIGN KEY (section14_row_id) REFERENCES mqa3_section14_rows(id) ON DELETE CASCADE
# );

# CREATE TABLE mqa3_section14_row_evaluation (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     section14_row_id INT NOT NULL,
#     evaluation TEXT NOT NULL,
#     FOREIGN KEY (section14_row_id) REFERENCES mqa3_section14_rows(id) ON DELETE CASCADE
# );

# -- ===========================
# -- SECTION 15: Weekly Schedule (ยุบตารางแรกสุดทิ้ง)
# -- ===========================
# CREATE TABLE mqa3_section15_rows (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     mqa3_id INT NOT NULL,
#     week INT NOT NULL,
#     topic TEXT NOT NULL,
#     hours INT NOT NULL,
#     activity TEXT NOT NULL,
#     teacher VARCHAR(255) NOT NULL,
#     FOREIGN KEY (mqa3_id) REFERENCES mqa3(id) ON DELETE CASCADE
# );

# CREATE TABLE mqa3_section15_row_clos (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     section15_row_id INT NOT NULL,
#     clo VARCHAR(100) NOT NULL,
#     FOREIGN KEY (section15_row_id) REFERENCES mqa3_section15_rows(id) ON DELETE CASCADE
# );

# -- ===========================
# -- SECTION 16: Assessment (ยุบตารางแรกสุดทิ้ง)
# -- ===========================
# CREATE TABLE mqa3_section16_rows (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     mqa3_id INT NOT NULL,
#     clo VARCHAR(100) NOT NULL,
#     learning TEXT NOT NULL,
#     assessment_weeks VARCHAR(100) NOT NULL,
#     FOREIGN KEY (mqa3_id) REFERENCES mqa3(id) ON DELETE CASCADE
# );

# CREATE TABLE mqa3_section16_row_activities (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     section16_row_id INT NOT NULL,
#     activity TEXT NOT NULL,
#     FOREIGN KEY (section16_row_id) REFERENCES mqa3_section16_rows(id) ON DELETE CASCADE
# );

# CREATE TABLE mqa3_section16_row_score_percents (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     section16_row_id INT NOT NULL,
#     score_percent INT NOT NULL,
#     FOREIGN KEY (section16_row_id) REFERENCES mqa3_section16_rows(id) ON DELETE CASCADE
# );

# -- ===========================
# -- SECTION 17: Agreements (ยุบตารางกลางทิ้ง)
# -- ===========================
# CREATE TABLE mqa3_section17_agreements (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     mqa3_id INT NOT NULL,
#     agreement TEXT NOT NULL,
#     FOREIGN KEY (mqa3_id) REFERENCES mqa3(id) ON DELETE CASCADE
# );

# -- ===========================
# -- SECTION 18: Course Integration (ยุบตารางกลางทิ้ง)
# -- ===========================
# CREATE TABLE mqa3_section18_integrations (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     mqa3_id INT NOT NULL,
#     course_integration TEXT NOT NULL,
#     FOREIGN KEY (mqa3_id) REFERENCES mqa3(id) ON DELETE CASCADE
# );

# -- ===========================
# -- SECTION 19: References (ยุบตารางกลางทิ้ง)
# -- ===========================
# CREATE TABLE mqa3_section19_textbooks (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     mqa3_id INT NOT NULL,
#     textbook TEXT NOT NULL,
#     FOREIGN KEY (mqa3_id) REFERENCES mqa3(id) ON DELETE CASCADE
# );

# CREATE TABLE mqa3_section19_online_sources (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     mqa3_id INT NOT NULL,
#     online_source TEXT NOT NULL,
#     FOREIGN KEY (mqa3_id) REFERENCES mqa3(id) ON DELETE CASCADE
# );