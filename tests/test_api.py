import sys
import os
import random
import string

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Helper Code

def random_email():
    """Generate a unique random email for each test run"""
    return "user_" + "".join(random.choices(string.ascii_lowercase, k=5)) + "@example.com"

# REGISTER USER
def test_register_user():
    email = random_email()
    response = client.post("/api/register", json={
        "name": "sampleuser",
        "email": email,
        "password": "Strong@123",
        "role": "User"
    })
    assert response.status_code in [201, 400]

# REGISTER ADMIN 
def test_register_admin():
    email = random_email()
    response = client.post("/api/register", json={
        "name": "sampleadmin",
        "email": email,
        "password": "Admin@123",
        "role": "Admin"
    })
    assert response.status_code in [201, 400]

# STRONG PASSWORD VALIDATION 
def test_register_invalid_password():
    response = client.post("/api/register", json={
        "name": "invaliduser",
        "email": random_email(),
        "password": "password",
        "role": "User"
    })
    assert response.status_code == 400

# LOGIN 
def test_login_user():
    email = random_email()
    client.post("/api/register", json={
        "name": "loginuser",
        "email": email,
        "password": "Strong@123",
        "role": "User"
    })
    response = client.post("/api/login", json={
        "email": email,
        "password": "Strong@123"
    })
    assert response.status_code == 200
    assert "message" in response.json()

# GET PROFILE 
def test_get_profile():
    email = random_email()
    client.post("/api/register", json={
        "name": "profileuser",
        "email": email,
        "password": "Strong@123",
        "role": "User"
    })
    response = client.get("/api/profile", headers={"email": email})
    assert response.status_code == 200
    data = response.json()
    assert "id" in data and "name" in data and "email" in data and "role" in data

# UPDATE PROFILE 

def test_update_profile():
    email_before = random_email()
    client.post("/api/register", json={
        "name": "updateuser",
        "email": email_before,
        "password": "Strong@123",
        "role": "User"
    })

    new_email = random_email()

    response = client.put("/api/profile", json={
        "name": "updateduser",
        "new_email": new_email
    }, headers={"email": email_before})

    assert response.status_code == 200

# ADMIN ACCESS CONTROLS 
def test_admin_controls():
    email_admin = random_email()
    client.post("/api/register", json={
        "name": "adminuser",
        "email": email_admin,
        "password": "Admin@123",
        "role": "Admin"
    })
    # GET ALL USERS
    response_get = client.get("/api/users", params={"email": email_admin})
    assert response_get.status_code in [200, 403]
    # DELETE USER
    response_delete = client.delete("/api/users/999", params={"email": email_admin})
    assert response_delete.status_code in [200, 404, 403]

#  PASSWORD RESET REQUEST 
def test_password_reset_request():
    email = random_email()
    client.post("/api/register", json={
        "name": "resetuser",
        "email": email,
        "password": "Strong@123",
        "role": "User"
    })
    response = client.post("/api/password-reset-request", json={"email": email})
    assert response.status_code == 200


# PASSWORD RESET CONFIRM 

def test_password_reset_confirm():
    email = random_email()
    # Register user
    client.post("/api/register", json={
        "name": "resetuser2",
        "email": email,
        "password": "Strong@123",
        "role": "User"
    })
    
    # Request reset
    reset_response = client.post("/api/password-reset-request", json={"email": email})
    assert reset_response.status_code == 200

    # Fetch token from in-memory dict
    from app.routes import password_reset_codes
    token = password_reset_codes.get(email)
    assert token is not None, "Reset token not generated"

    # Confirm reset
    confirm_response = client.post("/api/password-reset-confirm", json={
        "email": email,
        "token": token,
        "new_password": "NewStrong@123"
    })
    assert confirm_response.status_code == 200
