import pytest
from fastapi.testclient import TestClient
from main import app, LoginCredentials, get_db
import models, auth, schemas
from database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Dedicated test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_secureshop.db"
test_engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    
    admin = models.User(
        name="Admin User",
        email="admin@test.com",
        password_hash=auth.get_password_hash("Admin@123"),
        role="ADMIN"
    )
    user = models.User(
        name="Normal User",
        email="user@test.com",
        password_hash=auth.get_password_hash("User@123"),
        role="USER"
    )
    db.add_all([admin, user])
    
    products = [
        models.Product(name="Laptop", description="High performance laptop", price=999.99, stock=50),
        models.Product(name="Keyboard", description="Mechanical keyboard", price=89.99, stock=100),
        models.Product(name="Mouse", description="Wireless mouse", price=49.99, stock=150),
    ]
    db.add_all(products)
    db.commit()
    db.close()

# -------------------------------------------------------------
# Direct Unit / Integration Tests via Route Invocations & Logic
# -------------------------------------------------------------

def test_health_check():
    from main import health_check
    res = health_check()
    assert res["status"] == "healthy"
    assert res["service"] == "secureshop-backend"

def test_login_success():
    db = TestingSessionLocal()
    res = main_login(db, "user@test.com", "User@123")
    assert "access_token" in res
    assert res["token_type"] == "bearer"
    db.close()

def test_login_invalid():
    from main import login_json
    from fastapi import HTTPException
    db = TestingSessionLocal()
    with pytest.raises(HTTPException) as exc_info:
        login_json(LoginCredentials(email="user@test.com", password="wrongpassword"), db=db)
    assert exc_info.value.status_code == 401
    db.close()

def test_get_current_user_me():
    from main import read_users_me
    db = TestingSessionLocal()
    token = main_login(db, "user@test.com", "User@123")["access_token"]
    user = auth.get_current_user(token=token, db=db)
    me = read_users_me(current_user=user)
    assert me.email == "user@test.com"
    assert me.role == "USER"
    db.close()

def test_get_products():
    from main import read_products
    db = TestingSessionLocal()
    products = read_products(skip=0, limit=10, db=db)
    assert len(products) >= 3
    assert products[0].name == "Laptop"
    db.close()

def test_order_creation_and_listing():
    from main import create_order, read_orders
    db = TestingSessionLocal()
    token = main_login(db, "user@test.com", "User@123")["access_token"]
    user = auth.get_current_user(token=token, db=db)
    
    order_in = schemas.OrderCreate(product_id=1, quantity=2)
    order_out = create_order(order=order_in, current_user=user, db=db)
    assert order_out.id is not None
    assert order_out.total == 1999.98
    
    orders = read_orders(current_user=user, db=db)
    assert len(orders) >= 1
    assert orders[0].product_id == 1
    db.close()

def test_user_cannot_access_admin():
    from fastapi import HTTPException
    db = TestingSessionLocal()
    token = main_login(db, "user@test.com", "User@123")["access_token"]
    user = auth.get_current_user(token=token, db=db)
    
    with pytest.raises(HTTPException) as exc_info:
        auth.require_admin(current_user=user)
    assert exc_info.value.status_code == 403
    assert "permission" in exc_info.value.detail.lower()
    db.close()

def test_admin_can_access_admin_dashboard():
    from main import read_admin_dashboard
    db = TestingSessionLocal()
    token = main_login(db, "admin@test.com", "Admin@123")["access_token"]
    admin = auth.get_current_user(token=token, db=db)
    auth.require_admin(current_user=admin)
    
    dash = read_admin_dashboard(current_user=admin, db=db)
    assert dash["Total Users"] == 2
    assert dash["Total Products"] >= 3
    assert dash["System Status"] == "Operational"
    db.close()

def test_invalid_jwt_token():
    from fastapi import HTTPException
    db = TestingSessionLocal()
    with pytest.raises(HTTPException) as exc_info:
        auth.get_current_user(token="invalid.bearer.token", db=db)
    assert exc_info.value.status_code == 401
    db.close()

# Helper
def main_login(db, email, password):
    from main import login_json
    return login_json(LoginCredentials(email=email, password=password), db=db)
