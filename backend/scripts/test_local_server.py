import os
import sys
import asyncio
import httpx
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.main import app

async def run_tests():
    print("==================================================")
    print("[TEST] TESTING FASTAPI BACKEND SERVER LOCAL ENDPOINTS")
    print("==================================================")
    
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Health Check Endpoint
        print("\n1. Testing GET /health ...")
        res = await client.get("/health")
        print(f"Status Code: {res.status_code}")
        print(f"Response: {res.json()}")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        print("[SUCCESS] /health passed!")

        # 2. Papers Endpoint
        print("\n2. Testing GET /api/papers ...")
        res = await client.get("/api/papers")
        print(f"Status Code: {res.status_code}")
        papers_data = res.json()
        print(f"Response (Paper Count): {len(papers_data)}")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        print("[SUCCESS] /api/papers passed!")

        # 3. Auth Registration & Login
        print("\n3. Testing Auth Endpoints ...")
        test_username = "agnihotrianxh"
        test_password = "testpassword123"
        
        # Register (or ignore if already registered)
        reg_res = await client.post("/api/auth/register", json={"username": test_username, "password": test_password})
        print(f"Register Status Code: {reg_res.status_code}")

        # Login to get JWT Token
        token_res = await client.post("/api/auth/token", data={"username": test_username, "password": test_password})
        print(f"Token Status Code: {token_res.status_code}")
        assert token_res.status_code == 200, f"Token failed: {token_res.text}"
        token_data = token_res.json()
        access_token = token_data["access_token"]
        print(f"Access Token retrieved: {access_token[:25]}...")

        auth_headers = {"Authorization": f"Bearer {access_token}"}

        # 4. User Profile Endpoint /api/auth/me
        print("\n4. Testing GET /api/auth/me ...")
        me_res = await client.get("/api/auth/me", headers=auth_headers)
        print(f"Status Code: {me_res.status_code}")
        print(f"User Info: {me_res.json()}")
        assert me_res.status_code == 200, f"Expected 200, got {me_res.status_code}"
        print("[SUCCESS] /api/auth/me passed!")

        # 5. Notifications Endpoint (Authenticated)
        print("\n5. Testing GET /api/notifications ...")
        notif_res = await client.get("/api/notifications", headers=auth_headers)
        print(f"Status Code: {notif_res.status_code}")
        notif_list = notif_res.json()
        print(f"Notification count: {len(notif_list)}")
        assert notif_res.status_code == 200, f"Expected 200, got {notif_res.status_code}"
        print("[SUCCESS] /api/notifications passed!")

        # 6. Chat Endpoint (Agentic RAG Engine with Auth Header)
        print("\n6. Testing POST /api/chat ...")
        payload = {
            "question": "What are scaling laws in deep learning?",
            "session_id": "test_verification_session_101"
        }
        chat_res = await client.post("/api/chat", json=payload, headers=auth_headers)
        print(f"Status Code: {chat_res.status_code}")
        assert chat_res.status_code == 200, f"Expected 200, got {chat_res.text}"
        chat_data = chat_res.json()
        raw_response = chat_data.get('response', '')
        print(f"Response length: {len(raw_response)} characters")
        print("[SUCCESS] /api/chat passed!")

    print("\n==================================================")
    print("[SUCCESS] ALL BACKEND ENDPOINTS PASSED VERIFICATION CLEANLY!")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(run_tests())
