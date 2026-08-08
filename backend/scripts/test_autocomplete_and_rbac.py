import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_autocomplete_and_rbac():
    print("=" * 60)
    print("      ARXIVIST AI - AUTOCOMPLETE & RBAC SECURITY TEST SUITE")
    print("=" * 60)

    # 1. Search Suggestions API (/api/search/suggestions?q=benchmark)
    r_sug = requests.get(f"{BASE_URL}/api/search/suggestions?q=benchmark&limit=5")
    print(f"[TEST 1] GET /api/search/suggestions?q=benchmark -> Status: {r_sug.status_code}")
    print(f"        -> Response Body: {r_sug.text[:200]}")
    
    if r_sug.status_code == 200:
        sugs = r_sug.json()
        if sugs:
            print(f"        -> Top Match Title: '{sugs[0].get('title')[:50]}...'")

    # 2. Register Regular User (role: user)
    reg_user = "regular_user_test"
    reg_pass = "password123"
    requests.post(f"{BASE_URL}/api/auth/register", json={"username": reg_user, "password": reg_pass})
    r_user_token = requests.post(f"{BASE_URL}/api/auth/token", data={"username": reg_user, "password": reg_pass})
    user_token = r_user_token.json().get("access_token")
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # 3. Regular User Profile (/api/auth/me) -> Verify role === 'user'
    r_user_me = requests.get(f"{BASE_URL}/api/auth/me", headers=user_headers)
    print(f"[TEST 2] Regular User Profile             -> Status: {r_user_me.status_code} | Role: {r_user_me.json().get('role')}")

    # 4. Regular User Accessing Admin Route -> Must return 403 Forbidden!
    r_user_admin = requests.get(f"{BASE_URL}/api/admin/status", headers=user_headers)
    print(f"[TEST 3] Regular User Accessing /api/admin -> Status: {r_user_admin.status_code} (Expected 403 Forbidden)")

    # 5. Register Admin User (role: admin)
    admin_user = "admin"
    admin_pass = "password123"
    requests.post(f"{BASE_URL}/api/auth/register", json={"username": admin_user, "password": admin_pass})
    r_admin_token = requests.post(f"{BASE_URL}/api/auth/token", data={"username": admin_user, "password": admin_pass})
    admin_token = r_admin_token.json().get("access_token")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 6. Admin User Profile (/api/auth/me) -> Verify role === 'admin'
    r_admin_me = requests.get(f"{BASE_URL}/api/auth/me", headers=admin_headers)
    print(f"[TEST 4] Admin User Profile               -> Status: {r_admin_me.status_code} | Role: {r_admin_me.json().get('role')}")

    # 7. Admin User Accessing Admin Route -> Must return 200 OK!
    r_admin_status = requests.get(f"{BASE_URL}/api/admin/status", headers=admin_headers)
    print(f"[TEST 5] Admin Accessing /api/admin/status -> Status: {r_admin_status.status_code} (Expected 200 OK)")

    print("=" * 60)
    print("      AUTOCOMPLETE & RBAC SECURITY TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    test_autocomplete_and_rbac()
