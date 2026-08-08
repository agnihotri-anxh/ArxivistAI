import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from ..db.database import get_chats_collection

def get_user_chat_sessions(user_id: str) -> List[Dict[str, Any]]:
    """Returns a list of all chat sessions belonging to a user, sorted by updated_at descending."""
    chats_coll = get_chats_collection()
    cursor = chats_coll.find(
        {"user_id": user_id},
        {"_id": 0, "chat_id": 1, "user_id": 1, "title": 1, "created_at": 1, "updated_at": 1}
    ).sort("updated_at", -1)
    
    sessions = []
    for doc in cursor:
        sessions.append({
            "chat_id": doc.get("chat_id"),
            "title": doc.get("title", "Untitled Chat"),
            "created_at": doc.get("created_at", "").isoformat() if isinstance(doc.get("created_at"), datetime) else str(doc.get("created_at", "")),
            "updated_at": doc.get("updated_at", "").isoformat() if isinstance(doc.get("updated_at"), datetime) else str(doc.get("updated_at", ""))
        })
    return sessions

def create_chat_session(user_id: str, title: str = "New Research Chat") -> Dict[str, Any]:
    """Creates a new chat session for a user."""
    chats_coll = get_chats_collection()
    chat_id = f"chat_{uuid.uuid4().hex[:12]}"
    now = datetime.utcnow()
    
    doc = {
        "chat_id": chat_id,
        "user_id": user_id,
        "title": title,
        "created_at": now,
        "updated_at": now,
        "messages": [
            {
                "id": f"msg_{uuid.uuid4().hex[:8]}",
                "role": "assistant",
                "content": "Hello! I'm ArXivist AI, your research assistant. How can I assist you with academic papers today?",
                "timestamp": now.isoformat()
            }
        ]
    }
    chats_coll.insert_one(doc)
    
    return {
        "chat_id": chat_id,
        "user_id": user_id,
        "title": title,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
        "messages": doc["messages"]
    }

def get_chat_session(chat_id: str, user_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a specific chat session with its full message history."""
    chats_coll = get_chats_collection()
    doc = chats_coll.find_one({"chat_id": chat_id, "user_id": user_id}, {"_id": 0})
    if not doc:
        return None
    
    return {
        "chat_id": doc.get("chat_id"),
        "user_id": doc.get("user_id"),
        "title": doc.get("title", "Untitled Chat"),
        "created_at": doc.get("created_at", "").isoformat() if isinstance(doc.get("created_at"), datetime) else str(doc.get("created_at", "")),
        "updated_at": doc.get("updated_at", "").isoformat() if isinstance(doc.get("updated_at"), datetime) else str(doc.get("updated_at", "")),
        "messages": doc.get("messages", [])
    }

def add_message_to_chat(chat_id: str, user_id: str, role: str, content: str) -> Dict[str, Any]:
    """Appends a user or assistant message to a chat session and updates title if needed."""
    chats_coll = get_chats_collection()
    now = datetime.utcnow()
    msg_id = f"msg_{uuid.uuid4().hex[:8]}"
    
    message_entry = {
        "id": msg_id,
        "role": role,
        "content": content,
        "timestamp": now.isoformat()
    }
    
    # Fetch current chat to update title if it's the first user question
    chat = chats_coll.find_one({"chat_id": chat_id, "user_id": user_id})
    update_data: Dict[str, Any] = {
        "$push": {"messages": message_entry},
        "$set": {"updated_at": now}
    }
    
    if chat and role == "user":
        # If title is default or "New Research Chat", update title from question snippet
        if chat.get("title") in ["New Chat", "New Research Chat", "Untitled Chat"]:
            snippet = content.strip()[:40]
            if snippet:
                update_data["$set"]["title"] = snippet + ("..." if len(content) > 40 else "")
                
    chats_coll.update_one({"chat_id": chat_id, "user_id": user_id}, update_data)
    return message_entry

def delete_chat_session(chat_id: str, user_id: str) -> bool:
    """Deletes a chat session for a user."""
    chats_coll = get_chats_collection()
    res = chats_coll.delete_one({"chat_id": chat_id, "user_id": user_id})
    return res.deleted_count > 0
