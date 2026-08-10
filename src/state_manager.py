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

# ---new---

def save_audit(session_id: str, audit_data):
    """Saves the structured Pydantic audit into the database."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM domain_constraints WHERE session_id = ?", (session_id,))
        conn.execute("DELETE FROM project_dictionary WHERE session_id = ?", (session_id,))
        
        conn.execute(
            "INSERT INTO domain_constraints (session_id, domain, business_impact, deep_dive, risk_level) VALUES (?, ?, ?, ?, ?)",
            (session_id, "GLOBAL", audit_data.global_rationale, "See domain cards for specific architectural blockers.", audit_data.global_risk_score)
        )
        
        for constraint in audit_data.constraints:
            conn.execute(
                "INSERT INTO domain_constraints (session_id, domain, business_impact, deep_dive, risk_level) VALUES (?, ?, ?, ?, ?)",
                (session_id, constraint.domain, constraint.business_impact, constraint.deep_dive, constraint.risk_level)
            )
            
        # UPDATED: Now saving both term and definition
        for item in audit_data.jargon_caught:
            conn.execute(
                "INSERT INTO project_dictionary (session_id, term, definition) VALUES (?, ?, ?)",
                (session_id, item.term, item.definition)
            )
        conn.commit()

def get_domain_constraints(session_id: str):
    """Fetches all constraints for the active session."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT domain, business_impact, deep_dive, risk_level FROM domain_constraints WHERE session_id = ?", (session_id,))
        return cursor.fetchall()

def get_project_dictionary(session_id: str):
    """Fetches normalized terms and definitions for the active session."""
    with sqlite3.connect(DB_PATH) as conn:
        # UPDATED: Fetching the definition column as well
        cursor = conn.execute("SELECT term, definition FROM project_dictionary WHERE session_id = ?", (session_id,))
        return cursor.fetchall()

def get_chat_messages(session_id: str):
    """Fetches raw chat rows for the UI to render individual chat bubbles."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "SELECT role, message FROM chat_ledger WHERE session_id = ? ORDER BY timestamp ASC",
            (session_id,)
        )
        return cursor.fetchall()