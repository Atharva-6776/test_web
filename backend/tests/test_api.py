import pytest
from fastapi.testclient import TestClient
from main import app
from database import Base, engine, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_secureshop.db"
test_engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

Base.metadata.drop_all(bind=test_engine)
Base.metadata.create_all(bind=test_engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    # Seed data via the startup event equivalent
    from main import seed_data
    # Wait, we need to pass the override db to seed data, let's just seed manually
    import models, auth
    db = TestingSessionLocal()
    admin = models.User(name="Admin User", email="admin@test.com", password_hash=auth.get_password_hash("Admin@123"), role="ADMIN")
    user = models.User(name="Normal User", email="user@test.com", password_hash=auth.get_password_hash("User@123"), role="USER")
    db.add_all([admin, user])
    
    products = [
        models.Product(name="Laptop", description="High performance laptop", price=999.99, stock=50),
        models.Product(name="Keyboard", description="Mechanical keyboard", price=89.99, stock=100)
    ]
    db.add_all(products)
    db.commit()
    db.close()


def test_login_success():
    response = client.post("/api/auth/login", json={"email": "user@test.com", "password": "User@123"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_invalid():
    response = client.post("/api/auth/login", json={"email": "user@test.com", "password": "wrongpassword"})
    assert response.status_code == 401

def test_get_me():
    token = client.post("/api/auth/login", json={"email": "user@test.com", "password": "User@123"}).json()["access_token"]
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "user@test.com"

def test_get_products():
    response = client.get("/api/products")
    assert response.status_code == 200
    assert len(response.json()) >= 2

def test_orders():
    token = client.post("/api/auth/login", json={"email": "user@test.com", "password": "User@123"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create order
    response = client.post("/api/orders", json={"product_id": 1, "quantity": 2}, headers=headers)
    assert response.status_code == 200
    assert response.json()["total"] == 1999.98
    
    # Get orders
    response = client.get("/api/orders", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1

def test_admin_access():
    user_token = client.post("/api/auth/login", json={"email": "user@test.com", "password": "User@123"}).json()["access_token"]
    admin_token = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "Admin@123"}).json()["access_token"]
    
    # User tries admin
    resp1 = client.get("/api/admin/dashboard", headers={"Authorization": f"Bearer {user_token}"})
    assert resp1.status_code == 403
    
    # Admin tries admin
    resp2 = client.get("/api/admin/dashboard", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp2.status_code == 200
