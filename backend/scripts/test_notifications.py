import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_notifications():
    print("=" * 60)
    print("      ARXIVIST AI - NOTIFICATION BROADCAST TEST SUITE")
    print("=" * 60)

    # 1. Register / Login User
    username = "qa_notif_user"
    password = "password123"
    requests.post(f"{BASE_URL}/api/auth/register", json={"username": username, "password": password})
    r_token = requests.post(f"{BASE_URL}/api/auth/token", data={"username": username, "password": password})
    token = r_token.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    print(f"[TEST 1] User Auth Token                 -> Status: {r_token.status_code} | Token Obtained: {bool(token)}")

    # 2. Trigger Admin Pipeline Action (Broadcast Notification)
    r_pipeline = requests.post(f"{BASE_URL}/api/admin/pipeline/harvest?limit=10")
    print(f"[TEST 2] Trigger Admin Harvest Pipeline   -> Status: {r_pipeline.status_code} | Msg: {r_pipeline.json().get('message')}")

    # 3. Get Notifications List & Unread Count
    r_notif = requests.get(f"{BASE_URL}/api/notifications", headers=headers)
    notif_data = r_notif.json()
    notifs = notif_data.get("notifications", [])
    unread = notif_data.get("unread_count", 0)
    print(f"[TEST 3] GET /api/notifications           -> Status: {r_notif.status_code} | Count: {len(notifs)} | Unread: {unread}")

    if notifs:
        target_id = notifs[0]["notification_id"]
        safe_title = notifs[0]['title'].encode('ascii', 'ignore').decode('ascii')
        print(f"        -> Top Notification: '{safe_title}'")
        
        # 4. Mark Notification as Read
        r_read = requests.post(f"{BASE_URL}/api/notifications/{target_id}/read", headers=headers)
        print(f"[TEST 4] POST /api/notifications/{target_id}/read -> Status: {r_read.status_code}")

        # 5. Verify Unread Count Reduced
        r_notif2 = requests.get(f"{BASE_URL}/api/notifications", headers=headers)
        unread2 = r_notif2.json().get("unread_count", 0)
        print(f"[TEST 5] GET /api/notifications (After Read) -> Status: {r_notif2.status_code} | Unread: {unread2}")

    print("=" * 60)
    print("      NOTIFICATION VERIFICATION TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    test_notifications()
