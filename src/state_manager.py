import sqlite3
import uuid

DB_PATH = "naur_state.db"

def init_db():
    """Initializes the multi-tenant schema on server boot."""
    with open("src/schema_v2.sql", "r") as f:
        schema = f.read()
    
    with sqlite3.connect(DB_PATH) as conn:
        # Enable foreign key enforcement 
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.executescript(schema)
        conn.commit()

def create_session() -> str:
    """Generates a secure, isolated workspace for a new public user."""
    session_id = str(uuid.uuid4())
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO active_sessions (session_id) VALUES (?)", (session_id,))
        conn.commit()
    return session_id

def append_message(session_id: str, role: str, message: str):
    """Writes a message strictly to the user's isolated session ledger."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO chat_ledger (session_id, role, message) VALUES (?, ?, ?)",
            (session_id, role, message)
        )
        conn.commit()

def get_chat_ledger(session_id: str) -> str:
    """Retrieves only the chat history for the active session, formatted for the LLM."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "SELECT role, message FROM chat_ledger WHERE session_id = ? ORDER BY timestamp ASC",
            (session_id,)
        )
        rows = cursor.fetchall()
        
    if not rows:
        return "No communication logged yet."
        
    return "\n".join([f"{row[0]}: {row[1]}" for row in rows])

def clear_session_data(session_id: str):
    """
    Wipes the user's session. Because of ON DELETE CASCADE in the schema, 
    deleting the session automatically wipes their chat, constraints, and jargon.
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("DELETE FROM active_sessions WHERE session_id = ?", (session_id,))
        conn.commit()