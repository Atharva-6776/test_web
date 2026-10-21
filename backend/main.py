from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
import auth
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="SecureShop Test API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def seed_data():
    db = next(get_db())
    if not db.query(models.User).first():
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
        db.commit()

    if not db.query(models.Product).first():
        products = [
            models.Product(name="Laptop", description="High performance laptop", price=999.99, stock=50),
            models.Product(name="Keyboard", description="Mechanical keyboard", price=89.99, stock=100),
            models.Product(name="Mouse", description="Wireless mouse", price=49.99, stock=150),
            models.Product(name="Monitor", description="4K Monitor", price=299.99, stock=30),
            models.Product(name="Headphones", description="Noise cancelling headphones", price=199.99, stock=75),
        ]
        db.add_all(products)
        db.commit()

# --- Auth APIs ---
class LoginCredentials(schemas.BaseModel):
    email: str
    password: str

@app.post("/api/auth/login", response_model=schemas.Token)
def login_json(credentials: LoginCredentials, db: Session = Depends(get_db)):
    email = credentials.email
    password = credentials.password
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not auth.verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token_expires = auth.timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=schemas.UserOut)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@app.post("/api/auth/logout")
def logout():
    return {"message": "Successfully logged out"}

# --- Products API ---
@app.get("/api/products", response_model=List[schemas.ProductOut])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = db.query(models.Product).offset(skip).limit(limit).all()
    return products

# --- Orders API ---
@app.get("/api/orders", response_model=List[schemas.OrderOut])
def read_orders(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    if current_user.role == "ADMIN":
        orders = db.query(models.Order).all()
    else:
        orders = db.query(models.Order).filter(models.Order.user_id == current_user.id).all()
    return orders

@app.get("/api/orders/{order_id}", response_model=schemas.OrderOut)
def read_order(order_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if current_user.role != "ADMIN" and order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this order")
    return order

@app.post("/api/orders", response_model=schemas.OrderOut)
def create_order(order: schemas.OrderCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == order.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    total = product.price * order.quantity
    db_order = models.Order(
        user_id=current_user.id,
        product_id=order.product_id,
        quantity=order.quantity,
        total=total
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

# --- Admin API ---
@app.get("/api/admin/dashboard")
def read_admin_dashboard(current_user: models.User = Depends(auth.require_admin), db: Session = Depends(get_db)):
    total_users = db.query(models.User).count()
    total_products = db.query(models.Product).count()
    total_orders = db.query(models.Order).count()
    
    return {
        "Total Users": total_users,
        "Total Products": total_products,
        "Total Orders": total_orders,
        "System Status": "Operational"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
