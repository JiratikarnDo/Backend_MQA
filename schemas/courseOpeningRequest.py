# -- ===========================
# -- MAIN TABLE: COURSE OPENING REQUEST
# -- เก็บข้อมูลหลักของคำขอเปิดรายวิชา
# -- ===========================
# CREATE TABLE courseopeningrequest (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     `degreeLevel` VARCHAR(50) NOT NULL,
#     `requestScope` VARCHAR(50) NOT NULL,
#     `status` VARCHAR(50) NOT NULL DEFAULT 'draft',
#     `confirmStatus` VARCHAR(50) NOT NULL DEFAULT 'notConfirm',
#     `documentData` JSON NOT NULL,
#     semester VARCHAR(20) NULL,
#     `academicYear` VARCHAR(20) NULL,
#     `curriculumName` VARCHAR(255) NULL,
#     `majorName` VARCHAR(255) NULL,
#     `createdAt` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
#     `updatedAt` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
# );

# -- ===========================
# -- JSON STRUCTURE IN documentData
# -- เก็บรายละเอียดทุกส่วนของฟอร์มไว้ใน JSON ก้อนเดียว
# -- เพื่อให้ตรงกับ model/app และ ORM ปัจจุบัน
# -- ===========================
# {
#   "generalForm": {
#     "submissionRound": "string",
#     "semester": "string",
#     "academicYear": "string",
#     "curriculumName": "string",
#     "majorName": "string",
#     "programType": "string",
#     "studyPlan": "string",
#     "doctoralFormType": "string",
#     "formType": "string",
#     "campus": "string"
#   },
#   "studyForm": {
#     "learningPeriod": "string",
#     "campus": "string",
#     "targetGroup": "string",
#     "studyPlan": "string"
#   },
#   "yearBlocks": [
#     {
#       "yearLevel": "string",
#       "entryTerm": "string",
#       "academicYear": "string",
#       "subjectRows": [
#         {
#           "courseCode": "string",
#           "courseName": "string",
#           "credits": "string",
#           "groupCount": "string",
#           "studentCount": "string",
#           "isFreeElective": false,
#           "scienceTrack": false,
#           "humanitiesTrack": false,
#           "note": "string"
#         }
#       ]
#     }
#   ],
#   "approvalForm": {
#     "responsiblePeople": [
#       {
#         "name": "string",
#         "signedDate": "YYYY-MM-DD"
#       }
#     ],
#     "headName": "string",
#     "headDate": "YYYY-MM-DD",
#     "deputyDeanName": "string",
#     "deputyDeanDate": "YYYY-MM-DD",
#     "deanName": "string",
#     "deanDate": "YYYY-MM-DD",
#     "isConfirmed": false
#   }
# }

# -- ===========================
# -- SUMMARY FIELDS
# -- ดึงบางค่าจาก generalForm มาเก็บแยกเพื่อ query ได้ง่ายขึ้น
# -- ===========================
# semester       <- documentData.generalForm.semester
# academicYear   <- documentData.generalForm.academicYear
# curriculumName <- documentData.generalForm.curriculumName
# majorName      <- documentData.generalForm.majorName
