from app.db import get_db_connection, ensure_db_ready


def get_users_paginated(page: int, limit: int):
    ensure_db_ready()

    offset = (page - 1) * limit

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, name, email
        FROM users
        ORDER BY id
        LIMIT %s OFFSET %s;
        """,
        (limit, offset),
    )
    users = cur.fetchall()

    cur.execute("SELECT COUNT(*) FROM users;")
    total = cur.fetchone()[0]

    cur.close()
    conn.close()

    return users, total


def search_users_paginated(query: str, page: int, limit: int):
    ensure_db_ready()

    offset = (page - 1) * limit
    like_query = f"%{query.lower()}%"

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, name, email
        FROM users
        WHERE LOWER(name) LIKE %s
           OR LOWER(COALESCE(email, '')) LIKE %s
        ORDER BY id
        LIMIT %s OFFSET %s;
        """,
        (like_query, like_query, limit, offset),
    )
    users = cur.fetchall()

    cur.execute(
        """
        SELECT COUNT(*)
        FROM users
        WHERE LOWER(name) LIKE %s
           OR LOWER(COALESCE(email, '')) LIKE %s;
        """,
        (like_query, like_query),
    )
    total = cur.fetchone()[0]

    cur.close()
    conn.close()

    return users, total


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