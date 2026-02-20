# 🔐 User Management System API

A secure User Management System built using **FastAPI** and **PostgreSQL** with authentication, profile management, role-based access, and password reset functionality.

---

## 🚀 Tech Stack Used

- FastAPI
- PostgreSQL
- Psycopg2
- Passlib (bcrypt)
- Uvicorn
- Pytest
- Postman

---

## 📂 Project Features

- User Registration
- User Login
- Get User Profile
- Update Profile
- Admin Role Management
- Password Reset Request
- Password Reset Confirmation
- Secure Password Hashing
- Input Validation
- Unit Testing using Pytest
- API Testing using Postman

---

## ⚙️ Installation Steps

## Clone the Repository

```bash
git clone <your-repo-url>
cd USER_MANAGEMENT
```

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

---

## Install Dependencies

```bash
pip install fastapi uvicorn psycopg2 passlib[bcrypt] python-dotenv pytest
```

---

## Setup PostgreSQL Database

Create a database named:

```
user_management
```

Create table:

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password_hash TEXT,
    role VARCHAR(20)
);
```

---

## Run the Server

```bash
uvicorn app.main:app --reload
```

Server will run at:

```
http://127.0.0.1:8000
```

Swagger UI:

```
http://127.0.0.1:8000/docs
```

---

## 📬 API Endpoints

---

## 1. Register User

**POST**

```
/api/register
```

Body:

```json
{
  "name": "PostmanUser",
  "email": "postmanuser_new@example.com",
  "password": "Strong@123",
  "role": "User"
}
```

---

## 2. Login User

**POST**

```
/api/login
```

Body:

```json
{
  "email": "postmanuser_new@example.com",
  "password": "Strong@123"
}
```

---

## 3. Get Profile

**GET**

```
/api/profile
```

Headers:

| KEY   | VALUE                          |
|-------|--------------------------------|
| email | postmanuser_new@example.com    |

---

## 4. Update Profile

**PUT**

```
/api/profile
```

Headers:

| KEY   | VALUE                          |
|-------|--------------------------------|
| email | postmanuser_new@example.com    |

Body:

```json
{
  "name": "UpdatedUser",
  "new_email": "updatedmail@gmail.com"
}
```

---

## 5. Password Reset Request

**POST**

```
/api/password-reset-request
```

Body:

```json
{
  "email": "updatedmail@gmail.com"
}
```

Check Uvicorn terminal for 6-digit reset token.

---

## 6. Password Reset Confirm

**POST**

```
/api/password-reset-confirm
```

Body:

```json
{
  "email": "updatedmail@gmail.com",
  "token": "XXXXXX",
  "new_password": "Newpass@123"
}
```

---

## 7. Login With New Password

**POST**

```
/api/login
```

Body:

```json
{
  "email": "updatedmail@gmail.com",
  "password": "Newpass@123"
}
```

---

## Running Unit Tests

Run the following command:

```bash
pytest
```

You should see:

```
9 passed
```

---

## Password Rules

- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 number
- At least 1 special character

---

## Postman Collection

Test all APIs using Postman by creating requests for each endpoint with the above configurations.



## Notes

- Passwords are securely hashed using bcrypt.
- Email must be unique.
- Token for password reset is printed in terminal (mock email).

---

## Author

Tejaswi Ponnapalli

---
