import os
import uuid
from dotenv import load_dotenv

load_dotenv()

# Check if MSSQL is configured
MSSQL_SERVER = os.getenv("MSSQL_SERVER")
MSSQL_DATABASE = os.getenv("MSSQL_DATABASE")
MSSQL_USER = os.getenv("MSSQL_USER")
MSSQL_PASSWORD = os.getenv("MSSQL_PASSWORD")
MSSQL_PORT = int(os.getenv("MSSQL_PORT", "1433"))

USE_MSSQL = bool(MSSQL_SERVER and MSSQL_USER and MSSQL_PASSWORD)

if USE_MSSQL:
    import pymssql

    def get_connection():
        return pymssql.connect(
            server=MSSQL_SERVER,
            port=MSSQL_PORT,
            user=MSSQL_USER,
            password=MSSQL_PASSWORD,
            database=MSSQL_DATABASE,
            autocommit=True
        )

    def init_db():
        # Tables already verified/created via schema script
        pass

    def get_or_create_session(session_id=None, user_id=1):
        conn = get_connection()
        cursor = conn.cursor(as_dict=True)

        if session_id:
            cursor.execute(
                "SELECT session_id, user_id, title, created_at, updated_at, is_active FROM chatbot_sessions WHERE session_id = %s AND is_active = 1",
                (session_id,)
            )
            row = cursor.fetchone()
            if row:
                conn.close()
                return row

        new_session_id = session_id or str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO chatbot_sessions (session_id, user_id, title) VALUES (%s, %d, %s)",
            (new_session_id, int(user_id), "New Conversation")
        )
        cursor.execute(
            "SELECT session_id, user_id, title, created_at, updated_at, is_active FROM chatbot_sessions WHERE session_id = %s",
            (new_session_id,)
        )
        row = cursor.fetchone()
        conn.close()
        return row

    def add_message(session_id, sender, message, message_type="text"):
        conn = get_connection()
        cursor = conn.cursor(as_dict=True)
        cursor.execute(
            "INSERT INTO chatbot_messages (session_id, sender, message, message_type) VALUES (%s, %s, %s, %s)",
            (session_id, sender, message, message_type)
        )
        cursor.execute(
            "UPDATE chatbot_sessions SET updated_at = SYSUTCDATETIME() WHERE session_id = %s",
            (session_id,)
        )
        if sender == "user":
            cursor.execute(
                "SELECT COUNT(*) as cnt FROM chatbot_messages WHERE session_id = %s AND sender = 'user'",
                (session_id,)
            )
            count = cursor.fetchone()["cnt"]
            if count <= 1:
                title = message[:40] + ("..." if len(message) > 40 else "")
                cursor.execute(
                    "UPDATE chatbot_sessions SET title = %s WHERE session_id = %s",
                    (title, session_id)
                )
        conn.close()

    def get_recent_messages(session_id, limit=6):
        conn = get_connection()
        cursor = conn.cursor(as_dict=True)
        cursor.execute(
            f"""
            SELECT TOP {limit} sender, message 
            FROM chatbot_messages 
            WHERE session_id = %s 
            ORDER BY created_at DESC
            """,
            (session_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        messages = [dict(r) for r in rows]
        messages.reverse()
        return messages

    def get_user_conversations(user_id):
        conn = get_connection()
        cursor = conn.cursor(as_dict=True)
        cursor.execute(
            """
            SELECT 
                s.session_id,
                s.user_id,
                s.title,
                CONVERT(VARCHAR(25), s.created_at, 120) as created_at,
                CONVERT(VARCHAR(25), s.updated_at, 120) as updated_at,
                (SELECT TOP 1 m.message FROM chatbot_messages m WHERE m.session_id = s.session_id ORDER BY m.created_at DESC) as last_message
            FROM chatbot_sessions s
            WHERE s.user_id = %d AND s.is_active = 1
            ORDER BY s.updated_at DESC
            """,
            (int(user_id),)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_conversation_messages(session_id):
        conn = get_connection()
        cursor = conn.cursor(as_dict=True)
        cursor.execute(
            """
            SELECT id, sender, message_type, message, CONVERT(VARCHAR(25), created_at, 120) as created_at 
            FROM chatbot_messages 
            WHERE session_id = %s 
            ORDER BY created_at ASC
            """,
            (session_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_quick_suggestions():
        try:
            conn = get_connection()
            cursor = conn.cursor(as_dict=True)
            cursor.execute(
                "SELECT question_text FROM chatbot_quick_questions WHERE is_active = 1 ORDER BY display_order ASC"
            )
            rows = cursor.fetchall()
            conn.close()
            if rows:
                return [r["question_text"] for r in rows]
        except Exception:
            pass
        return [
            "How to check my loan eligibility?",
            "What is a good CIBIL / credit score?",
            "How does a Personal Loan work?",
            "What is a Mutual Fund and SIP?",
            "Connect to CredVisor Manager"
        ]

else:
    import sqlite3

    DB_PATH = os.getenv("CHATBOT_DB_PATH", "chatbot.db")

    def get_connection():
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS chatbot_sessions (
            session_id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            title TEXT DEFAULT 'New Conversation',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS chatbot_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            sender TEXT NOT NULL,
            message_type TEXT DEFAULT 'text',
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.commit()
        conn.close()

    def get_or_create_session(session_id=None, user_id=1):
        conn = get_connection()
        cursor = conn.cursor()
        if session_id:
            cursor.execute("SELECT * FROM chatbot_sessions WHERE session_id = ? AND is_active = 1", (session_id,))
            row = cursor.fetchone()
            if row:
                conn.close()
                return dict(row)
        new_session_id = session_id or str(uuid.uuid4())
        cursor.execute("INSERT INTO chatbot_sessions (session_id, user_id, title) VALUES (?, ?, ?)", (new_session_id, int(user_id), "New Conversation"))
        conn.commit()
        cursor.execute("SELECT * FROM chatbot_sessions WHERE session_id = ?", (new_session_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row)

    def add_message(session_id, sender, message, message_type="text"):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO chatbot_messages (session_id, sender, message, message_type) VALUES (?, ?, ?, ?)", (session_id, sender, message, message_type))
        cursor.execute("UPDATE chatbot_sessions SET updated_at = CURRENT_TIMESTAMP WHERE session_id = ?", (session_id,))
        if sender == "user":
            cursor.execute("SELECT COUNT(*) as cnt FROM chatbot_messages WHERE session_id = ? AND sender = 'user'", (session_id,))
            count = cursor.fetchone()["cnt"]
            if count <= 1:
                title = message[:40] + ("..." if len(message) > 40 else "")
                cursor.execute("UPDATE chatbot_sessions SET title = ? WHERE session_id = ?", (title, session_id))
        conn.commit()
        conn.close()

    def get_recent_messages(session_id, limit=6):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT sender, message FROM chatbot_messages WHERE session_id = ? ORDER BY created_at DESC LIMIT ?", (session_id, limit))
        rows = cursor.fetchall()
        conn.close()
        messages = [dict(r) for r in rows]
        messages.reverse()
        return messages

    def get_user_conversations(user_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.session_id, s.user_id, s.title, s.created_at, s.updated_at,
                   (SELECT m.message FROM chatbot_messages m WHERE m.session_id = s.session_id ORDER BY m.created_at DESC LIMIT 1) as last_message
            FROM chatbot_sessions s WHERE s.user_id = ? AND s.is_active = 1 ORDER BY s.updated_at DESC
        """, (int(user_id),))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_conversation_messages(session_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, sender, message_type, message, created_at FROM chatbot_messages WHERE session_id = ? ORDER BY created_at ASC", (session_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def delete_conversation(session_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE chatbot_sessions SET is_active = 0 WHERE session_id = ?", (session_id,))
        conn.commit()
        conn.close()
        return True

    init_db()
