from app.db import get_db_connection, ensure_db_ready


def get_all_users():
    ensure_db_ready()

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, name, email FROM users ORDER BY id;")
    users = cur.fetchall()

    cur.close()
    conn.close()

    return users


def get_user_by_id(user_id):
    ensure_db_ready()

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, name, email FROM users WHERE id = %s;", (user_id,))
    user = cur.fetchone()

    cur.close()
    conn.close()

    return user


def add_user_to_db(name, email):
    ensure_db_ready()

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id, name, email;",
        (name, email),
    )
    user = cur.fetchone()
    conn.commit()

    cur.close()
    conn.close()

    return user


def update_user_in_db(user_id, name, email):
    ensure_db_ready()

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE users
        SET name = %s, email = %s
        WHERE id = %s
        RETURNING id, name, email;
        """,
        (name, email, user_id),
    )
    user = cur.fetchone()
    conn.commit()

    cur.close()
    conn.close()

    return user


def delete_user_from_db(user_id):
    ensure_db_ready()

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM users WHERE id = %s RETURNING id;", (user_id,))
    deleted_user = cur.fetchone()
    conn.commit()

    cur.close()
    conn.close()

    return deleted_user