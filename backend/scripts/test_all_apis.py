import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_suite():
    print("=" * 60)
    print("      ARXIVIST AI - COMPREHENSIVE ENDPOINT VERIFICATION")
    print("=" * 60)
    
    # 1. Health Check
    try:
        r = requests.get(f"{BASE_URL}/health")
        print(f"[API 1] GET /health                    -> Status: {r.status_code} | Output: {r.json()}")
    except Exception as e:
        print(f"[API 1] GET /health FAILED: {e}")

    # 2. Registration
    reg_username = "test_qa_user"
    reg_password = "password123"
    try:
        r = requests.post(f"{BASE_URL}/api/auth/register", json={"username": reg_username, "password": reg_password})
        print(f"[API 2] POST /api/auth/register        -> Status: {r.status_code} | Output: {r.text[:80]}")
    except Exception as e:
        print(f"[API 2] POST /api/auth/register FAILED: {e}")

    # 3. Login / Token
    token = None
    try:
        r = requests.post(f"{BASE_URL}/api/auth/token", data={"username": reg_username, "password": reg_password})
        data = r.json()
        token = data.get("access_token")
        print(f"[API 3] POST /api/auth/token           -> Status: {r.status_code} | Token Obtained: {bool(token)}")
    except Exception as e:
        print(f"[API 3] POST /api/auth/token FAILED: {e}")

    # 4. Authenticated User Profile (/api/auth/me)
    if token:
        try:
            r = requests.get(f"{BASE_URL}/api/auth/me", headers={"Authorization": f"Bearer {token}"})
            print(f"[API 4] GET /api/auth/me               -> Status: {r.status_code} | User: {r.json().get('username')}")
        except Exception as e:
            print(f"[API 4] GET /api/auth/me FAILED: {e}")

    # 5. Papers Catalog Query (/api/papers)
    try:
        r = requests.get(f"{BASE_URL}/api/papers?limit=5")
        papers = r.json()
        print(f"[API 5] GET /api/papers                -> Status: {r.status_code} | Papers Count: {len(papers)} | First Title: {papers[0]['title'][:40]}...")
    except Exception as e:
        print(f"[API 5] GET /api/papers FAILED: {e}")

    # 6. Admin Status Metrics (/api/admin/status)
    try:
        r = requests.get(f"{BASE_URL}/api/admin/status")
        metrics = r.json()
        print(f"[API 6] GET /api/admin/status          -> Status: {r.status_code}")
        print(f"        -> Staging: {metrics.get('raw_staging_count')} | Catalog: {metrics.get('website_papers_count')} | Milvus: {metrics.get('milvus_vectors_count')} | Users: {metrics.get('users_count')}")
    except Exception as e:
        print(f"[API 6] GET /api/admin/status FAILED: {e}")

    # 7. PDF Static File Serving (/api/pdfs/{filename})
    try:
        r = requests.get(f"{BASE_URL}/api/pdfs/2607.08768v1.pdf")
        print(f"[API 7] GET /api/pdfs/2607.08768v1.pdf -> Status: {r.status_code} | Content-Type: {r.headers.get('Content-Type')}")
    except Exception as e:
        print(f"[API 7] GET /api/pdfs FAILED: {e}")

    # 8. RAG Chatbot Endpoint (/api/chat)
    if token:
        try:
            r = requests.post(
                f"{BASE_URL}/api/chat",
                headers={"Authorization": f"Bearer {token}"},
                json={"question": "What is scaling law in LLMs?"}
            )
            print(f"[API 8] POST /api/chat                 -> Status: {r.status_code} | Answer snippet: {r.json().get('answer', '')[:80]}...")
        except Exception as e:
            print(f"[API 8] POST /api/chat FAILED: {e}")

    print("=" * 60)
    print("      ALL API TESTS EXECUTED COMPREHENSIVELY!")
    print("=" * 60)

if __name__ == "__main__":
    test_suite()
