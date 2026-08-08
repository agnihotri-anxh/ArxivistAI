import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from ..db.database import get_notifications_collection

def broadcast_ingestion_notification(
    count: int,
    action_type: str = "harvest",
    sample_titles: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Broadcasts a notification to all users when new research papers are ingested by the admin."""
    notifs_coll = get_notifications_collection()
    notif_id = f"notif_{uuid.uuid4().hex[:12]}"
    now = datetime.utcnow()

    title_preview = ""
    if sample_titles and len(sample_titles) > 0:
        clean_sample = sample_titles[0][:60] + ("..." if len(sample_titles[0]) > 60 else "")
        title_preview = f" Sample: '{clean_sample}'"

    title = f"NEW: {count} New Research Papers Ingested!"
    message = f"Admin recently ran pipeline task '{action_type}' and added {count} new research paper records.{title_preview}"

    doc = {
        "notification_id": notif_id,
        "title": title,
        "message": message,
        "type": "new_papers_ingested",
        "action_type": action_type,
        "paper_count": count,
        "created_at": now,
        "read_by": []
    }
    notifs_coll.insert_one(doc)
    print(f"[Notification] Broadcasted alert for {count} new papers.")
    return {
        "notification_id": notif_id,
        "title": title,
        "message": message,
        "type": "new_papers_ingested",
        "created_at": now.isoformat(),
        "read_by": []
    }

def get_user_notifications(user_id: Optional[str] = None) -> Dict[str, Any]:
    """Retrieves all notifications and calculates unread count for the given user."""
    notifs_coll = get_notifications_collection()
    cursor = notifs_coll.find({}, {"_id": 0}).sort("created_at", -1).limit(50)
    
    notifications = []
    unread_count = 0
    
    for doc in cursor:
        read_by_list = doc.get("read_by", [])
        is_read = bool(user_id and user_id in read_by_list)
        if not is_read:
            unread_count += 1
            
        notifications.append({
            "notification_id": doc.get("notification_id"),
            "title": doc.get("title"),
            "message": doc.get("message"),
            "type": doc.get("type", "system"),
            "paper_count": doc.get("paper_count", 0),
            "created_at": doc.get("created_at", "").isoformat() if isinstance(doc.get("created_at"), datetime) else str(doc.get("created_at", "")),
            "is_read": is_read
        })
        
    return {
        "notifications": notifications,
        "unread_count": unread_count
    }

def mark_notification_as_read(notification_id: str, user_id: str) -> bool:
    """Marks a notification as read for a specific user."""
    if not user_id:
        return False
    notifs_coll = get_notifications_collection()
    res = notifs_coll.update_one(
        {"notification_id": notification_id},
        {"$addToSet": {"read_by": user_id}}
    )
    return res.modified_count > 0
