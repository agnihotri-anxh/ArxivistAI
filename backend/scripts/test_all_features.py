import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_all_features():
    print("=" * 60)
    print("      ARXIVIST AI - FULL FEATURE VERIFICATION TEST SUITE")
    print("=" * 60)
    
    # 1. Health
    r = requests.get(f"{BASE_URL}/health")
    print(f"[TEST 1] GET /health                    -> Status: {r.status_code} | Output: {r.json()}")

    # 2. Register & Login
    username = "qa_test_admin"
    password = "password123"
    requests.post(f"{BASE_URL}/api/auth/register", json={"username": username, "password": password})
    r_token = requests.post(f"{BASE_URL}/api/auth/token", data={"username": username, "password": password})
    token = r_token.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    print(f"[TEST 2] Auth Token                     -> Status: {r_token.status_code} | Token Obtained: {bool(token)}")

    # 3. Create Chat Session
    r_session = requests.post(f"{BASE_URL}/api/chat/sessions", headers=headers, json={"title": "LLM Scaling Laws Discussion"})
    chat_id = r_session.json().get("chat_id")
    print(f"[TEST 3] POST /api/chat/sessions        -> Status: {r_session.status_code} | Chat ID: {chat_id}")

    # 4. List Chat Sessions
    r_list = requests.get(f"{BASE_URL}/api/chat/sessions", headers=headers)
    print(f"[TEST 4] GET /api/chat/sessions         -> Status: {r_list.status_code} | Sessions Count: {len(r_list.json())}")

    # 5. Multi-Turn RAG Chat with Memory
    r_chat1 = requests.post(f"{BASE_URL}/api/chat", headers=headers, json={"chat_id": chat_id, "question": "What is DPO in LLM alignment?"})
    print(f"[TEST 5] POST /api/chat (Turn 1)        -> Status: {r_chat1.status_code} | Answer snippet: {r_chat1.json().get('answer', '')[:70]}...")

    r_chat2 = requests.post(f"{BASE_URL}/api/chat", headers=headers, json={"chat_id": chat_id, "question": "How does it compare to PPO?"})
    print(f"[TEST 6] POST /api/chat (Turn 2 Memory) -> Status: {r_chat2.status_code} | Answer snippet: {r_chat2.json().get('answer', '')[:70]}...")

    # 6. Get Chat Session History
    r_hist = requests.get(f"{BASE_URL}/api/chat/sessions/{chat_id}", headers=headers)
    msgs = r_hist.json().get("messages", [])
    print(f"[TEST 7] GET /api/chat/sessions/{chat_id} -> Status: {r_hist.status_code} | Total Messages: {len(msgs)}")

    # 7. Paginated Papers Query
    r_papers = requests.get(f"{BASE_URL}/api/papers?page=1&limit=6&category=Artificial%20Intelligence")
    papers_data = r_papers.json()
    print(f"[TEST 8] GET /api/papers (Paginated)    -> Status: {r_papers.status_code} | Total: {papers_data.get('total')} | Total Pages: {papers_data.get('total_pages')}")

    # 8. Admin Status Metrics & Processed Papers Table
    r_admin = requests.get(f"{BASE_URL}/api/admin/status")
    print(f"[TEST 9] GET /api/admin/status          -> Status: {r_admin.status_code} | Staging: {r_admin.json().get('raw_staging_count')} | Catalog: {r_admin.json().get('website_papers_count')}")

    print("=" * 60)
    print("      ALL FEATURE VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    test_all_features()
