import pytest
import httpx
from uuid import uuid4

BASE_URL = "http://localhost:8000/api"

@pytest.fixture
def test_user():
    return {
        "email": f"test_{uuid4().hex[:8]}@example.com",
        "password": "testpass123",
        "name": "Test User",
    }

@pytest.fixture
def client():
    return httpx.Client(base_url=BASE_URL, timeout=10)

def get_token(client, user):
    client.post("/auth/register", json=user)
    r = client.post("/auth/login", json={
        "email": user["email"],
        "password": user["password"],
    })
    return r.json()["access_token"]

class TestAuth:
    def test_register_and_login(self, client, test_user):
        r = client.post("/auth/register", json=test_user)
        assert r.status_code == 201
        data = r.json()
        assert data["email"] == test_user["email"]
        assert "id" in data

        r2 = client.post("/auth/login", json={
            "email": test_user["email"],
            "password": test_user["password"],
        })
        assert r2.status_code == 200
        assert "access_token" in r2.json()

    def test_get_me(self, client, test_user):
        token = get_token(client, test_user)
        r = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        assert r.json()["email"] == test_user["email"]

class TestCompanies:
    def test_crud(self, client, test_user):
        token = get_token(client, test_user)
        headers = {"Authorization": f"Bearer {token}"}
        name = f"Test Corp {uuid4().hex[:6]}"

        r = client.post("/companies", json={"name": name, "industry": "Tech", "status": "active"}, headers=headers)
        assert r.status_code in (200, 201)
        cid = r.json()["id"]
        assert r.json()["name"] == name

        r = client.get("/companies", headers=headers)
        assert r.status_code == 200
        assert any(c["id"] == cid for c in r.json()["items"])

        r = client.get(f"/companies/{cid}", headers=headers)
        assert r.status_code == 200
        assert r.json()["name"] == name

        r = client.put(f"/companies/{cid}", json={"name": f"{name} Updated"}, headers=headers)
        assert r.status_code == 200
        assert r.json()["name"] == f"{name} Updated"

        r = client.delete(f"/companies/{cid}", headers=headers)
        assert r.status_code == 200

        r = client.get(f"/companies/{cid}", headers=headers)
        assert r.status_code == 404

class TestContacts:
    def test_crud(self, client, test_user):
        token = get_token(client, test_user)
        headers = {"Authorization": f"Bearer {token}"}

        cname = f"Parent Co {uuid4().hex[:6]}"
        r = client.post("/companies", json={"name": cname}, headers=headers)
        cid = r.json()["id"]

        email = f"contact_{uuid4().hex[:6]}@test.com"
        r = client.post("/contacts", json={
            "name": "John Doe",
            "email": email,
            "phone": "123456789",
            "position": "Manager",
            "company_id": cid,
        }, headers=headers)
        assert r.status_code in (200, 201)
        contact_id = r.json()["id"]
        assert "company_name" in r.json()

        r = client.get("/contacts", headers=headers)
        assert r.status_code == 200
        assert any(c["id"] == contact_id for c in r.json()["items"])

        r = client.put(f"/contacts/{contact_id}", json={"name": "Jane Doe"}, headers=headers)
        assert r.status_code == 200
        assert r.json()["name"] == "Jane Doe"

        r = client.delete(f"/contacts/{contact_id}", headers=headers)
        assert r.status_code == 200

class TestProjects:
    def test_crud(self, client, test_user):
        token = get_token(client, test_user)
        headers = {"Authorization": f"Bearer {token}"}

        cname = f"Proj Co {uuid4().hex[:6]}"
        r = client.post("/companies", json={"name": cname}, headers=headers)
        cid = r.json()["id"]

        r = client.post("/projects", json={
            "project_name": "Website Redesign",
            "budget": 50000,
            "status": "active",
            "company_id": cid,
        }, headers=headers)
        assert r.status_code in (200, 201)
        pid = r.json()["id"]
        assert "company_name" in r.json()
        assert r.json()["project_name"] == "Website Redesign"

        r = client.get("/projects", headers=headers)
        assert r.status_code == 200
        assert any(p["id"] == pid for p in r.json()["items"])

        r = client.put(f"/projects/{pid}", json={"budget": 75000}, headers=headers)
        assert r.status_code == 200
        assert r.json()["budget"] == 75000

        r = client.delete(f"/projects/{pid}", headers=headers)
        assert r.status_code == 200

class TestLeads:
    def test_crud_and_status(self, client, test_user):
        token = get_token(client, test_user)
        headers = {"Authorization": f"Bearer {token}"}

        r = client.post("/leads", json={
            "company_name": f"Lead Co {uuid4().hex[:6]}",
            "phone": "555-0100",
            "source": "website",
            "notes": "Interested in product",
        }, headers=headers)
        assert r.status_code in (200, 201)
        lid = r.json()["id"]

        r = client.get("/leads", headers=headers)
        assert r.status_code == 200
        assert any(l["id"] == lid for l in r.json()["items"])

        r = client.put(f"/leads/{lid}", json={"status": "QUALIFIED"}, headers=headers)
        assert r.status_code == 200
        assert r.json()["status"] == "QUALIFIED"

class TestQuotes:
    def test_crud_and_pdf(self, client, test_user):
        token = get_token(client, test_user)
        headers = {"Authorization": f"Bearer {token}"}

        r = client.post("/quotes", json={
            "customer_name": "Test Customer",
            "customer_email": "customer@test.com",
            "product": "Consulting Service",
            "quantity": 10,
            "unit_price": 1500,
        }, headers=headers)
        assert r.status_code in (200, 201)
        qid = r.json()["id"]
        assert r.json()["total_price"] == 15000

        r = client.get("/quotes", headers=headers)
        assert r.status_code == 200
        assert any(q["id"] == qid for q in r.json()["items"])

        r = client.get(f"/quotes/{qid}/pdf", headers=headers)
        assert r.status_code == 200
        assert r.headers["content-type"] == "application/pdf"

        r = client.put(f"/quotes/{qid}", json={"status": "SENT"}, headers=headers)
        assert r.status_code == 200
        assert r.json()["status"] == "SENT"

class TestDashboard:
    def test_stats(self, client, test_user):
        token = get_token(client, test_user)
        r = client.get("/dashboard", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        data = r.json()
        assert "companies_total" in data
        assert "contacts_total" in data
        assert "projects_total" in data
        assert "active_leads" in data
        assert "leads_by_status" in data
        assert "recent_activities" in data

class TestAnalytics:
    def test_overview(self, client, test_user):
        token = get_token(client, test_user)
        r = client.get("/analytics/overview", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        data = r.json()
        assert "quotes_trend" in data
        assert "leads_by_status" in data
        assert "leads_by_source" in data

class TestKnowledge:
    def test_crud(self, client, test_user):
        token = get_token(client, test_user)
        headers = {"Authorization": f"Bearer {token}"}

        r = client.post("/knowledge", json={
            "title": f"Article {uuid4().hex[:6]}",
            "content": "Test article content",
            "category": "general",
        }, headers=headers)
        assert r.status_code in (200, 201)
        kid = r.json()["id"]

        r = client.get("/knowledge", headers=headers)
        assert r.status_code == 200
        assert any(k["id"] == kid for k in r.json()["items"])

        r = client.get(f"/knowledge/{kid}", headers=headers)
        assert r.status_code == 200

        r = client.put(f"/knowledge/{kid}", json={"title": "Updated Article"}, headers=headers)
        assert r.status_code == 200
        assert r.json()["title"] == "Updated Article"

        r = client.delete(f"/knowledge/{kid}", headers=headers)
        assert r.status_code == 200

        r = client.get(f"/knowledge/{kid}", headers=headers)
        assert r.status_code == 404

class TestTasks:
    def test_crud(self, client, test_user):
        token = get_token(client, test_user)
        headers = {"Authorization": f"Bearer {token}"}

        r = client.post("/tasks", json={
            "title": f"Task {uuid4().hex[:6]}",
            "description": "Test task description",
        }, headers=headers)
        assert r.status_code in (200, 201)
        tid = r.json()["id"]

        r = client.get("/tasks", headers=headers)
        assert r.status_code == 200
        assert any(t["id"] == tid for t in r.json()["items"])

        r = client.put(f"/tasks/{tid}", json={"status": "completed"}, headers=headers)
        assert r.status_code == 200
        assert r.json()["status"] == "completed"

        r = client.delete(f"/tasks/{tid}", headers=headers)
        assert r.status_code == 200

class TestAssistant:
    def test_chat(self, client, test_user):
        token = get_token(client, test_user)
        r = client.post("/assistant/chat", json={
            "message": "Hello, how are you?",
        }, headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        data = r.json()
        assert "reply" in data
        assert "suggestions" in data
