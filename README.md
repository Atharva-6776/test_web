# SecureShop Test Application

This is a standalone, lightweight e-commerce application built for testing the **Adaptive Cyber Defense Framework**. It contains standard web vulnerabilities by design (as it lacks security measures) so that the Gateway/Framework can protect it.

## Architecture

```
USER
  ↓
Adaptive Cyber Defense Gateway (External)
  ↓
SecureShop Test Application
  ↓
FastAPI Backend (Port 8000)
  ↓
SQLite Database (Local)
```

## Folder Structure

```
secure-shop-test/
├── backend/
│   ├── main.py        # FastAPI entry point
│   ├── auth.py        # Authentication & JWT
│   ├── models.py      # SQLAlchemy Models
│   ├── schemas.py     # Pydantic Schemas
│   ├── database.py    # DB connection setup
│   ├── tests/         # Pytest test cases
│   └── requirements.txt
└── frontend/
    ├── src/           # React source code (Pages, Components)
    ├── package.json   # NPM dependencies
    └── vite.config.ts # Vite configuration
```

## Backend Setup

1. Open a terminal and navigate to the `backend/` directory:
   ```bash
   cd secure-shop-test/backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install fastapi uvicorn sqlalchemy bcrypt pyjwt python-multipart pytest httpx email-validator pydantic[email]
   ```
4. Run the backend server:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

*Note: The database (`secureshop.db`) and test users/products will be automatically created on startup.*

## Frontend Setup

1. Open a new terminal and navigate to the `frontend/` directory:
   ```bash
   cd secure-shop-test/frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```

## Environment Variables

- **Frontend:** You can create a `.env` file in the `frontend` folder with `VITE_API_URL=http://localhost:8000` to point to a different backend URL. It defaults to `http://localhost:8000`.
- **Backend:** The secret key and algorithm are hardcoded in `auth.py` for simplicity in this test application.

## Database Setup

SQLite is used for simplicity. The database file `secureshop.db` will be created automatically in the `backend/` directory when the server starts.

## Test Credentials

**Admin User:**
- Email: `admin@test.com`
- Password: `Admin@123`

**Normal User:**
- Email: `user@test.com`
- Password: `User@123`

## API List

**Auth**
- `POST /api/auth/login` - Authenticate and receive JWT
- `GET /api/auth/me` - Get current user profile
- `POST /api/auth/logout` - Logout

**Products**
- `GET /api/products` - List all products

**Orders**
- `GET /api/orders` - List orders for the current user (Admin sees all)
- `GET /api/orders/{id}` - Get order by ID
- `POST /api/orders` - Create a new order

**Admin**
- `GET /api/admin/dashboard` - Get system statistics (Requires ADMIN role)

## How to Test Each Page

1. **Login Page (`/login`):** Try logging in with the test credentials above.
2. **Dashboard (`/dashboard`):** Check your statistics. If logged in as Admin, you will see an Admin panel shortcut.
3. **Products (`/products`):** View the dummy products. Click "Order Now" to create an order.
4. **Orders (`/orders`):** View the orders you just placed.
5. **Profile (`/profile`):** View your account details and use the Logout button.
6. **Admin Panel (`/admin`):** Accessible only via the Admin account. If a normal user navigates here, they will see an "Access Denied" error (HTTP 403).

## Reverse Proxy / Security Gateway Integration

When placing this application behind your **Adaptive Cyber Defense Framework**:

1. Configure your Gateway to forward traffic to `http://localhost:8000` (Backend API).
2. The frontend should be configured (via `.env`) to point its `VITE_API_URL` to your Gateway's URL instead of `localhost:8000`.
3. The Gateway will inspect requests, enforce RBAC, block IPs, or reroute attackers to honeypots before forwarding legitimate traffic to the SecureShop backend.
