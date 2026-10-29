def test_dashboard_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Dashboard" in response.data

def test_add_student(client):
    response = client.post("/students", data={
        "roll_number": "S002", "name": "Test Student", "email": "test@example.com"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Test Student" in response.data

def test_students_requires_roll_and_name(client):
    response = client.post("/students", data={"roll_number": "", "name": ""}, follow_redirects=True)
    assert response.status_code == 200
    assert b"required" in response.data.lower() or b"Roll number and name are required" in response.data

def test_reports_csv(client):
    response = client.get("/reports.csv")
    assert response.status_code == 200
    assert b"Roll Number" in response.data
