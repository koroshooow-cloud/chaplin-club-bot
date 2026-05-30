import sqlite3

DB_NAME = "reservations.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        session INTEGER NOT NULL,
        table_number INTEGER NOT NULL,
        guests INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def create_reservation(
    user_id,
    name,
    phone,
    session_number,
    table_number,
    guests
):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO reservations
    (
        user_id,
        name,
        phone,
        session,
        table_number,
        guests
    )
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        name,
        phone,
        session_number,
        table_number,
        guests
    ))

    conn.commit()
    conn.close()


def get_user_reservations(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT
        id,
        session,
        table_number,
        guests
    FROM reservations
    WHERE user_id = ?
    ORDER BY id DESC
    """, (user_id,))

    rows = cur.fetchall()

    conn.close()

    return rows


def delete_reservation(reservation_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM reservations WHERE id = ?",
        (reservation_id,)
    )

    conn.commit()
    conn.close()


def is_table_reserved(session_number, table_number):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT COUNT(*)
    FROM reservations
    WHERE session = ?
    AND table_number = ?
    """, (
        session_number,
        table_number
    ))

    count = cur.fetchone()[0]

    conn.close()

    return count > 0
