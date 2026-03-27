import sqlite3
import hashlib
import os
from datetime import datetime

DB_PATH = "marketplace.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('client', 'tasker')),
            bio TEXT DEFAULT '',
            location TEXT DEFAULT '',
            avatar_emoji TEXT DEFAULT '👤',
            rating REAL DEFAULT 0.0,
            review_count INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            icon TEXT NOT NULL,
            description TEXT
        );

        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category_id INTEGER NOT NULL,
            location TEXT NOT NULL,
            budget REAL NOT NULL,
            scheduled_date TEXT NOT NULL,
            status TEXT DEFAULT 'open' CHECK(status IN ('open', 'assigned', 'completed', 'cancelled')),
            tasker_id INTEGER,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (client_id) REFERENCES users(id),
            FOREIGN KEY (category_id) REFERENCES categories(id),
            FOREIGN KEY (tasker_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS offers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            tasker_id INTEGER NOT NULL,
            price REAL NOT NULL,
            message TEXT NOT NULL,
            status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'accepted', 'rejected')),
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (task_id) REFERENCES tasks(id),
            FOREIGN KEY (tasker_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            reviewer_id INTEGER NOT NULL,
            reviewee_id INTEGER NOT NULL,
            rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
            comment TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (task_id) REFERENCES tasks(id),
            FOREIGN KEY (reviewer_id) REFERENCES users(id),
            FOREIGN KEY (reviewee_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            task_id INTEGER,
            content TEXT NOT NULL,
            is_read INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (sender_id) REFERENCES users(id),
            FOREIGN KEY (receiver_id) REFERENCES users(id)
        );
    """)

    # Seed categories if empty
    c.execute("SELECT COUNT(*) FROM categories")
    if c.fetchone()[0] == 0:
        categories = [
            ("Temizlik", "🧹", "Ev ve ofis temizliği"),
            ("Taşımacılık", "📦", "Eşya taşıma ve nakliyat"),
            ("Tadilat & Bakım", "🔨", "Ev tamiri ve bakım işleri"),
            ("Bahçe & Dış Alan", "🌿", "Bahçe düzenleme ve bakım"),
            ("Montaj", "🔧", "Mobilya ve cihaz montajı"),
            ("Temizlik & Çamaşır", "👕", "Çamaşır ve ütü hizmetleri"),
            ("Teknoloji", "💻", "Bilgisayar ve teknoloji desteği"),
            ("Eğitim & Özel Ders", "📚", "Ders verme ve eğitim"),
            ("Güzellik & Kişisel Bakım", "💄", "Kuaför ve kişisel bakım"),
            ("Diğer", "✨", "Diğer hizmetler"),
        ]
        c.executemany(
            "INSERT INTO categories (name, icon, description) VALUES (?, ?, ?)",
            categories,
        )

    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# --- Users ---

def create_user(name, email, password, role, location="", bio=""):
    conn = get_conn()
    c = conn.cursor()
    avatars = {"client": "🧑", "tasker": "👷"}
    try:
        c.execute(
            "INSERT INTO users (name, email, password_hash, role, location, bio, avatar_emoji) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, email, hash_password(password), role, location, bio, avatars.get(role, "👤")),
        )
        conn.commit()
        return c.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def login_user(email, password):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=? AND password_hash=?", (email, hash_password(password)))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def get_user(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def update_user_profile(user_id, name, bio, location):
    conn = get_conn()
    conn.execute("UPDATE users SET name=?, bio=?, location=? WHERE id=?", (name, bio, location, user_id))
    conn.commit()
    conn.close()


def get_top_taskers(limit=6):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM users WHERE role='tasker' ORDER BY rating DESC, review_count DESC LIMIT ?",
        (limit,),
    )
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# --- Categories ---

def get_categories():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM categories ORDER BY name")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# --- Tasks ---

def create_task(client_id, title, description, category_id, location, budget, scheduled_date):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO tasks (client_id, title, description, category_id, location, budget, scheduled_date) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (client_id, title, description, category_id, location, budget, scheduled_date),
    )
    conn.commit()
    task_id = c.lastrowid
    conn.close()
    return task_id


def get_tasks(status="open", category_id=None, search=None):
    conn = get_conn()
    c = conn.cursor()
    query = """
        SELECT t.*, u.name as client_name, u.avatar_emoji as client_avatar,
               cat.name as category_name, cat.icon as category_icon
        FROM tasks t
        JOIN users u ON t.client_id = u.id
        JOIN categories cat ON t.category_id = cat.id
        WHERE t.status=?
    """
    params = [status]
    if category_id:
        query += " AND t.category_id=?"
        params.append(category_id)
    if search:
        query += " AND (t.title LIKE ? OR t.description LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    query += " ORDER BY t.created_at DESC"
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_task(task_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT t.*, u.name as client_name, u.avatar_emoji as client_avatar, u.location as client_location,
               cat.name as category_name, cat.icon as category_icon
        FROM tasks t
        JOIN users u ON t.client_id = u.id
        JOIN categories cat ON t.category_id = cat.id
        WHERE t.id=?
    """, (task_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def get_client_tasks(client_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT t.*, cat.name as category_name, cat.icon as category_icon,
               u2.name as tasker_name
        FROM tasks t
        JOIN categories cat ON t.category_id = cat.id
        LEFT JOIN users u2 ON t.tasker_id = u2.id
        WHERE t.client_id=?
        ORDER BY t.created_at DESC
    """, (client_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def complete_task(task_id):
    conn = get_conn()
    conn.execute("UPDATE tasks SET status='completed' WHERE id=?", (task_id,))
    conn.commit()
    conn.close()


def cancel_task(task_id):
    conn = get_conn()
    conn.execute("UPDATE tasks SET status='cancelled' WHERE id=?", (task_id,))
    conn.commit()
    conn.close()


# --- Offers ---

def create_offer(task_id, tasker_id, price, message):
    conn = get_conn()
    c = conn.cursor()
    # Check duplicate
    c.execute("SELECT id FROM offers WHERE task_id=? AND tasker_id=?", (task_id, tasker_id))
    if c.fetchone():
        conn.close()
        return None
    c.execute(
        "INSERT INTO offers (task_id, tasker_id, price, message) VALUES (?, ?, ?, ?)",
        (task_id, tasker_id, price, message),
    )
    conn.commit()
    offer_id = c.lastrowid
    conn.close()
    return offer_id


def get_task_offers(task_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT o.*, u.name as tasker_name, u.avatar_emoji as tasker_avatar,
               u.rating as tasker_rating, u.review_count as tasker_reviews,
               u.location as tasker_location
        FROM offers o
        JOIN users u ON o.tasker_id = u.id
        WHERE o.task_id=?
        ORDER BY o.created_at DESC
    """, (task_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_tasker_offers(tasker_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT o.*, t.title as task_title, t.status as task_status,
               t.scheduled_date, t.location as task_location,
               u.name as client_name
        FROM offers o
        JOIN tasks t ON o.task_id = t.id
        JOIN users u ON t.client_id = u.id
        WHERE o.tasker_id=?
        ORDER BY o.created_at DESC
    """, (tasker_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def accept_offer(offer_id, task_id, tasker_id):
    conn = get_conn()
    conn.execute("UPDATE offers SET status='accepted' WHERE id=?", (offer_id,))
    conn.execute("UPDATE offers SET status='rejected' WHERE task_id=? AND id!=?", (task_id, offer_id))
    conn.execute("UPDATE tasks SET status='assigned', tasker_id=? WHERE id=?", (tasker_id, task_id))
    conn.commit()
    conn.close()


def reject_offer(offer_id):
    conn = get_conn()
    conn.execute("UPDATE offers SET status='rejected' WHERE id=?", (offer_id,))
    conn.commit()
    conn.close()


# --- Reviews ---

def create_review(task_id, reviewer_id, reviewee_id, rating, comment):
    conn = get_conn()
    c = conn.cursor()
    # Check duplicate
    c.execute("SELECT id FROM reviews WHERE task_id=? AND reviewer_id=?", (task_id, reviewer_id))
    if c.fetchone():
        conn.close()
        return None
    c.execute(
        "INSERT INTO reviews (task_id, reviewer_id, reviewee_id, rating, comment) VALUES (?, ?, ?, ?, ?)",
        (task_id, reviewer_id, reviewee_id, rating, comment),
    )
    # Update user rating
    c.execute(
        "UPDATE users SET rating = (SELECT AVG(rating) FROM reviews WHERE reviewee_id=?), "
        "review_count = (SELECT COUNT(*) FROM reviews WHERE reviewee_id=?) WHERE id=?",
        (reviewee_id, reviewee_id, reviewee_id),
    )
    conn.commit()
    conn.close()
    return True


def get_user_reviews(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT r.*, u.name as reviewer_name, u.avatar_emoji as reviewer_avatar,
               t.title as task_title
        FROM reviews r
        JOIN users u ON r.reviewer_id = u.id
        JOIN tasks t ON r.task_id = t.id
        WHERE r.reviewee_id=?
        ORDER BY r.created_at DESC
    """, (user_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def has_reviewed(task_id, reviewer_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id FROM reviews WHERE task_id=? AND reviewer_id=?", (task_id, reviewer_id))
    result = c.fetchone() is not None
    conn.close()
    return result


# --- Messages ---

def send_message(sender_id, receiver_id, content, task_id=None):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO messages (sender_id, receiver_id, task_id, content) VALUES (?, ?, ?, ?)",
        (sender_id, receiver_id, task_id, content),
    )
    conn.commit()
    conn.close()


def get_conversation(user1_id, user2_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT m.*, u.name as sender_name, u.avatar_emoji as sender_avatar
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE (m.sender_id=? AND m.receiver_id=?) OR (m.sender_id=? AND m.receiver_id=?)
        ORDER BY m.created_at ASC
    """, (user1_id, user2_id, user2_id, user1_id))
    rows = c.fetchall()
    # Mark as read
    conn.execute(
        "UPDATE messages SET is_read=1 WHERE sender_id=? AND receiver_id=?",
        (user2_id, user1_id),
    )
    conn.commit()
    conn.close()
    return [dict(r) for r in rows]


def get_conversations(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT DISTINCT
            CASE WHEN m.sender_id=? THEN m.receiver_id ELSE m.sender_id END as other_id,
            u.name as other_name, u.avatar_emoji as other_avatar, u.role as other_role,
            MAX(m.created_at) as last_message_time,
            SUM(CASE WHEN m.receiver_id=? AND m.is_read=0 THEN 1 ELSE 0 END) as unread_count
        FROM messages m
        JOIN users u ON u.id = CASE WHEN m.sender_id=? THEN m.receiver_id ELSE m.sender_id END
        WHERE m.sender_id=? OR m.receiver_id=?
        GROUP BY other_id
        ORDER BY last_message_time DESC
    """, (user_id, user_id, user_id, user_id, user_id))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_unread_count(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM messages WHERE receiver_id=? AND is_read=0", (user_id,))
    count = c.fetchone()[0]
    conn.close()
    return count
