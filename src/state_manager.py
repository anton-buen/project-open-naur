"""
Persistence and session isolation layer for multi-tenant architecture ledger.

Manages isolated user workspaces via SQLite, providing strict session boundaries
for chat histories, domain constraints, and terminology dictionaries. All operations
respect foreign key cascading to maintain referential integrity.
"""

import sqlite3
import uuid
from typing import List, Tuple

DB_PATH = "naur_state.db"


def init_db() -> None:
    """
    Initialize the multi-tenant SQLite schema on server boot.

    Reads schema_v2.sql and executes it against the database connection,
    enforcing foreign key constraints for strict referential integrity.
    """
    with open("src/schema_v2.sql", "r") as f:
        schema = f.read()

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.executescript(schema)
        conn.commit()


def create_session() -> str:
    """
    Generate a secure, isolated workspace for a new user.

    Args:
        None

    Returns:
        str: A UUID4 session identifier guaranteeing isolation from other users.
    """
    session_id = str(uuid.uuid4())
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO active_sessions (session_id) VALUES (?)", (session_id,))
        conn.commit()
    return session_id


def append_message(session_id: str, role: str, message: str) -> None:
    """
    Write a message to the user's isolated session ledger.

    Args:
        session_id (str): The user's session UUID.
        role (str): The persona/role contributing to the thread (e.g., "Frontend Engineer").
        message (str): The message content.
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO chat_ledger (session_id, role, message) VALUES (?, ?, ?)",
            (session_id, role, message),
        )
        conn.commit()


def get_chat_ledger(session_id: str) -> str:
    """
    Retrieve the full chat history for a session, formatted for LLM input.

    Args:
        session_id (str): The user's session UUID.

    Returns:
        str: Formatted chat log or "No communication logged yet." if empty.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "SELECT role, message FROM chat_ledger WHERE session_id = ? ORDER BY timestamp ASC",
            (session_id,),
        )
        rows = cursor.fetchall()

    if not rows:
        return "No communication logged yet."

    return "\n".join([f"{row[0]}: {row[1]}" for row in rows])


def clear_session_data(session_id: str) -> None:
    """
    Wipe all session data via cascading delete.

    ON DELETE CASCADE in the schema ensures that deleting an active_sessions row
    automatically purges all associated chat_ledger, domain_constraints, and
    project_dictionary rows.

    Args:
        session_id (str): The user's session UUID to purge.
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("DELETE FROM active_sessions WHERE session_id = ?", (session_id,))
        conn.commit()


def save_audit(session_id: str, audit_data) -> None:
    """
    Persist the structured architectural audit results to the ledger.

    Clears previous audit results and inserts a new global summary, per-domain
    constraints, and caught terminology into the database.

    Args:
        session_id (str): The user's session UUID.
        audit_data (ArchitecturalAudit): Validated Pydantic audit model.
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM domain_constraints WHERE session_id = ?", (session_id,))
        conn.execute("DELETE FROM project_dictionary WHERE session_id = ?", (session_id,))

        conn.execute(
            "INSERT INTO domain_constraints (session_id, domain, business_impact, deep_dive, risk_level) VALUES (?, ?, ?, ?, ?)",
            (
                session_id,
                "GLOBAL",
                audit_data.global_rationale,
                "See domain cards for specific architectural blockers.",
                audit_data.global_risk_score,
            ),
        )

        for constraint in audit_data.constraints:
            conn.execute(
                "INSERT INTO domain_constraints (session_id, domain, business_impact, deep_dive, risk_level) VALUES (?, ?, ?, ?, ?)",
                (
                    session_id,
                    constraint.domain,
                    constraint.business_impact,
                    constraint.deep_dive,
                    constraint.risk_level,
                ),
            )

        for item in audit_data.jargon_caught:
            conn.execute(
                "INSERT INTO project_dictionary (session_id, term, definition) VALUES (?, ?, ?)",
                (session_id, item.term, item.definition),
            )
        conn.commit()


def get_domain_constraints(session_id: str) -> List[Tuple[str, str, str, str]]:
    """
    Fetch all domain constraints for a session.

    Args:
        session_id (str): The user's session UUID.

    Returns:
        List[Tuple[str, str, str, str]]: Rows of (domain, business_impact, deep_dive, risk_level).
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "SELECT domain, business_impact, deep_dive, risk_level FROM domain_constraints WHERE session_id = ?",
            (session_id,),
        )
        return cursor.fetchall()


def get_project_dictionary(session_id: str) -> List[Tuple[str, str]]:
    """
    Fetch all normalized terminology for a session.

    Args:
        session_id (str): The user's session UUID.

    Returns:
        List[Tuple[str, str]]: Rows of (term, definition).
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "SELECT term, definition FROM project_dictionary WHERE session_id = ?",
            (session_id,),
        )
        return cursor.fetchall()


def get_chat_messages(session_id: str) -> List[Tuple[str, str, str]]:
    """
    Fetch raw chat rows with timestamps for UI rendering.

    Args:
        session_id (str): The user's session UUID.

    Returns:
        List[Tuple[str, str, str]]: Rows of (role, message, timestamp).
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "SELECT role, message, timestamp FROM chat_ledger WHERE session_id = ? ORDER BY timestamp ASC",
            (session_id,),
        )
        return cursor.fetchall()