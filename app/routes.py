from fastapi import APIRouter, HTTPException, Header , Body
from app.models import UserRegister, UserLogin, UserUpdate, PasswordResetRequest, PasswordResetConfirm
from app.database import get_connection
from app.auth import hash_password, verify_password
from psycopg2.extras import RealDictCursor
import re
import random
import string


from psycopg2 import errors


router = APIRouter(prefix="/api")

# In-memory storage for password reset codes
password_reset_codes = {}


# User Registration

@router.post("/register", status_code=201)
def register_user(user: UserRegister):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Check if email already exists
    cursor.execute("SELECT * FROM users WHERE email = %s", (user.email,))
    existing_user = cursor.fetchone()
    if existing_user:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Email already registered")

    # Strong password validation
    password = user.password
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
    if not re.search(r"[A-Z]", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one lowercase letter")
    if not re.search(r"[0-9]", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one number")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one special character")

    # Role validation
    if user.role not in ["User", "Admin"]:
        raise HTTPException(status_code=400, detail="Role must be 'User' or 'Admin'")

    hashed_password = hash_password(password)

    cursor.execute(
        "INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
        (user.name, user.email, hashed_password, user.role)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "User registered successfully"}



# Login

@router.post("/login")
def login_user(user: UserLogin):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("SELECT * FROM users WHERE email = %s", (user.email,))
    db_user = cursor.fetchone()
    if not db_user:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid email or password")

    stored_password = db_user["password_hash"]
    if not verify_password(user.password, stored_password):
        cursor.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid email or password")

    cursor.close()
    conn.close()
    return {"message": "Login successful"}


# Get Profile


@router.get("/profile")
def get_profile(email: str = Header(...)):

    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("SELECT id, name, email, role FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user



# Update Profile



@router.put("/profile")
def update_profile(
    email: str = Header(...),
    name: str = Body(None),
    new_email: str = Body(None)
):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        if name:
            cursor.execute("UPDATE users SET name=%s WHERE email=%s", (name, email))


        if new_email:
            cursor.execute("UPDATE users SET email=%s WHERE email=%s", (new_email, email))

        conn.commit()

    except errors.UniqueViolation:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Email already exists")

    cursor.close()
    conn.close()

    return {"message": "Profile updated successfully"}


# Get All Users (Admin Only)

@router.get("/users")
def get_all_users(email: str):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("SELECT role FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    if not user:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    if user["role"] != "Admin":
        cursor.close()
        conn.close()
        raise HTTPException(status_code=403, detail="Access denied")

    cursor.execute("SELECT id, name, email, role FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return users



# Delete User (Admin Only)

@router.delete("/users/{user_id}")
def delete_user(user_id: int, email: str):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("SELECT role FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    if not user:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    if user["role"] != "Admin":
        cursor.close()
        conn.close()
        raise HTTPException(status_code=403, detail="Access denied")

    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    target_user = cursor.fetchone()
    if not target_user:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="User to delete not found")

    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "User deleted successfully"}



# Password Reset Request

@router.post("/password-reset-request")
def password_reset_request(data: PasswordResetRequest):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("SELECT * FROM users WHERE email = %s", (data.email,))
    user = cursor.fetchone()
    if not user:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Email not registered")

    # Generate mock reset code
    code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    password_reset_codes[data.email] = code
    print(f"[Mock Email] Password reset code for {data.email}: {code}")

    cursor.close()
    conn.close()
    return {"message": "Password reset code sent (mock email)"}



# Password Reset Confirm

@router.post("/password-reset-confirm")
def password_reset_confirm(data: PasswordResetConfirm):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    stored_code = password_reset_codes.get(data.email)
    if not stored_code:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=400, detail="No reset request found")
    if stored_code != data.token:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid reset token")

    password = data.new_password
    if len(password) < 8 or \
       not re.search(r"[A-Z]", password) or \
       not re.search(r"[a-z]", password) or \
       not re.search(r"[0-9]", password) or \
       not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        cursor.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Password does not meet complexity requirements")

    hashed = hash_password(password)
    cursor.execute("UPDATE users SET password_hash = %s WHERE email = %s", (hashed, data.email))
    conn.commit()
    password_reset_codes.pop(data.email, None)
    cursor.close()
    conn.close()

    return {"message": "Password reset successfully"}
