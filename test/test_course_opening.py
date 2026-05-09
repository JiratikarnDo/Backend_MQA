import pytest
from fastapi.testclient import TestClient

def test_create_opening_request_out_of_deadline(client: TestClient, admin_token):
    response = client.post(
        "/course-opening/",
        json={
            "semester": "ภาค 1",
            "academic_year": 2099,
            "curriculum_name": "เทสหลักสูตร",
            "program_type": "4 ปี",
            "study_mode": "ภาคปกติ",
            "campus": "บางพระ",
            "target_group": "BP",
            "requested_courses": []
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "ขณะนี้ไม่อยู่ในช่วงเวลาที่เปิดให้ยื่นคำร้อง"

def test_pagination_logic(client: TestClient, admin_token):
    response = client.get("/course/?page=1&size=2", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert len(response.json()) <= 2