# SecureShop Integration Specification for Adaptive Cyber Defense Framework (ACDF)

**Document Version:** 1.1.0  
**Status:** Verified & Active  
**Author:** SecureShop Engineering Team  

---

## 1. Executive Summary & Architecture

SecureShop is a clean, realistic e-commerce application serving as the protected upstream application target for the **Adaptive Cyber Defense Framework (ACDF)**.

SecureShop does **not** implement defensive honeypots, rate limiting, IP blocking, or WAF rules internally — all threat detection, MTD (Moving Target Defense), and filtering are handled by ACDF sitting as the reverse proxy in front.

```text
  [ Client / Browser / Attacker ]
                 │
                 ▼
  ┌────────────────────────────────────────────────────────┐
  │   Adaptive Cyber Defense Framework (ACDF Gateway)      │
  │   Listening: Port 8000                                 │
  │                                                        │
  │  • WAF Inspection (SQLi, XSS, Path Traversal)          │
  │  • IP Blacklisting & Risk Scoring                      │
  │  • Honeypot & Decoy Traps (/gateway/api/admin/debug)   │
  │  • MTD Route Mutation (/api/v1/d/{token})              │
  └──────────────────────────┬─────────────────────────────┘
                             │ Reverse Proxy Forward
                             ▼
  ┌────────────────────────────────────────────────────────┐
  │   SecureShop Test Application (Upstream)               │
  │   Listening: Port 8001                                 │
  │                                                        │
  │  • GET  /health (Health check)                         │
  │  • POST /api/auth/login                                │
  │  • GET  /api/auth/me                                   │
  │  • GET  /api/products                                  │
  │  • GET  /api/orders & POST /api/orders                 │
  │  • GET  /api/admin/dashboard (RBAC: ADMIN only)        │
  └────────────────────────────────────────────────────────┘
```

---

## 2. Server Entry Point & Network Binding

- **Root Directory:** `secure-shop-test/backend`
- **Application Entry Point:** `main.py` (`app = FastAPI(...)`)
- **Default Upstream Port:** `8001` (Configured via `PORT=8001`)
- **Default Upstream Host:** `0.0.0.0` or `127.0.0.1` (Configured via `HOST=0.0.0.0`)
- **Start Command:**
  ```powershell
  uvicorn main:app --host 0.0.0.0 --port 8001 --reload
  ```

---

## 3. Configuration & Environment Variables

SecureShop reads configuration from environment variables or `.env`:

| Variable | Default Value | Description |
|---|---|---|
| `PORT` | `8001` | TCP port for FastAPI backend server |
| `HOST` | `0.0.0.0` | Host IP binding address |
| `DATABASE_URL` | `sqlite:///./secureshop.db` | SQLAlchemy database URL |
| `JWT_SECRET_KEY` | *(32-byte secret)* | HMAC-SHA256 signing key for JWT tokens |
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Token expiration lifetime |
| `ALLOWED_ORIGINS` | `http://localhost:5173,...` | Comma-delimited list of CORS allowed origins |

### ACDF Gateway Upstream Configuration:
In ACDF's `.env`, configure:
```env
SECURESHOP_UPSTREAM_URL=http://127.0.0.1:8001
```

> **Note on Cloud / Vercel Deployments:**  
> If ACDF is hosted remotely (e.g., on Vercel or Render), `127.0.0.1` is **not** reachable. SecureShop must be assigned a public HTTPS URL (e.g., deployed to Render, Koyeb, or exposed via an SSH/ngrok tunnel), and `SECURESHOP_UPSTREAM_URL` must point to that public HTTPS address.

---

## 4. API Endpoints & Expected HTTP Behavior

### Health Check
- **`GET /health`** (or `GET /api/health`)
  - **Auth Required:** No
  - **Response (`200 OK`):**
    ```json
    {
      "status": "healthy",
      "service": "secureshop-backend",
      "version": "1.0.0"
    }
    ```

### Authentication
- **`POST /api/auth/login`**
  - **Body (`application/json`):**
    ```json
    {
      "email": "user@test.com",
      "password": "User@123"
    }
    ```
  - **Success (`200 OK`):**
    ```json
    {
      "access_token": "<jwt_string>",
      "token_type": "bearer"
    }
    ```
  - **Failure (`401 Unauthorized`):** Invalid password or non-existent email.

- **`GET /api/auth/me`**
  - **Headers:** `Authorization: Bearer <jwt_token>`
  - **Success (`200 OK`):**
    ```json
    {
      "id": 2,
      "name": "Normal User",
      "email": "user@test.com",
      "role": "USER",
      "status": "ACTIVE"
    }
    ```
  - **Failure (`401 Unauthorized`):** Missing or invalid JWT.

- **`POST /api/auth/logout`**
  - **Response (`200 OK`):** `{"message": "Successfully logged out"}`

### Product Catalog
- **`GET /api/products`**
  - **Auth Required:** No
  - **Query Params:** `skip` (default 0), `limit` (default 100)
  - **Response (`200 OK`):**
    ```json
    [
      {
        "id": 1,
        "name": "Laptop",
        "description": "High performance laptop",
        "price": 999.99,
        "stock": 50
      }
    ]
    ```

### Orders / Checkout
- **`GET /api/orders`**
  - **Headers:** `Authorization: Bearer <jwt_token>`
  - **Behavior:** Returns only the current user's orders (or all orders if user has `ADMIN` role).
- **`POST /api/orders`**
  - **Headers:** `Authorization: Bearer <jwt_token>`
  - **Body:** `{"product_id": 1, "quantity": 2}`
  - **Response (`200 OK`):** Returns the created order object with calculated `total`.
  - **Failure (`404 Not Found`):** Product does not exist.

### Administration
- **`GET /api/admin/dashboard`**
  - **Headers:** `Authorization: Bearer <jwt_token>`
  - **Success (`200 OK` for ADMIN):**
    ```json
    {
      "Total Users": 2,
      "Total Products": 5,
      "Total Orders": 0,
      "System Status": "Operational"
    }
    ```
  - **Forbidden (`403 Forbidden` for USER):**
    ```json
    {
      "detail": "You do not have permission to access this page."
    }
    ```

---

## 5. Pre-seeded Test Accounts

These accounts are initialized automatically upon backend startup:

| Role | Email | Password |
|---|---|---|
| **ADMIN** | `admin@test.com` | `Admin@123` |
| **USER** | `user@test.com` | `User@123` |

---

## 6. Verification & Test Commands

Run the test suite inside `secure-shop-test/backend`:

```powershell
cd secure-shop-test\backend
.\venv\Scripts\activate
pytest tests/test_api.py -v
```

**Test Suite Coverage:**
1. `test_health_check` — Verifies `/health` endpoint responds with 200 and correct payload.
2. `test_login_success` — Verifies valid credentials return valid JWT.
3. `test_login_invalid` — Verifies bad credentials return HTTP 401.
4. `test_get_current_user_me` — Verifies `/api/auth/me` resolves profile from JWT.
5. `test_get_products` — Verifies product catalog retrieval.
6. `test_order_creation_and_listing` — Verifies checkout order placement and list filtering.
7. `test_user_cannot_access_admin` — Verifies non-admin users receive HTTP 403 Forbidden.
8. `test_admin_can_access_admin_dashboard` — Verifies admin users receive HTTP 200 OK.
9. `test_invalid_jwt_token` — Verifies forged/corrupt tokens return HTTP 401.
