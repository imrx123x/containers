from app.db import ensure_db_ready, get_db_connection


def _row_to_dict(row):
    return {
        "id": row[0],
        "name": row[1],
        "email": row[2],
        "role": row[3],
        "created_at": row[4],
        "updated_at": row[5],
    }


def _row_to_auth_dict(row):
    return {
        "id": row[0],
        "name": row[1],
        "email": row[2],
        "password_hash": row[3],
        "role": row[4],
        "created_at": row[5],
        "updated_at": row[6],
    }


def get_users_paginated(page: int, limit: int):
    ensure_db_ready()

    offset = (page - 1) * limit

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, name, email, role, created_at, updated_at
        FROM users
        ORDER BY id
        LIMIT %s OFFSET %s;
        """,
        (limit, offset),
    )
    users = [_row_to_dict(row) for row in cur.fetchall()]

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
        SELECT id, name, email, role, created_at, updated_at
        FROM users
        WHERE LOWER(name) LIKE %s
           OR LOWER(COALESCE(email, '')) LIKE %s
        ORDER BY id
        LIMIT %s OFFSET %s;
        """,
        (like_query, like_query, limit, offset),
    )
    users = [_row_to_dict(row) for row in cur.fetchall()]

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

    cur.execute(
        """
        SELECT id, name, email, role, created_at, updated_at
        FROM users
        WHERE id = %s;
        """,
        (user_id,),
    )
    row = cur.fetchone()

    cur.close()
    conn.close()

    return _row_to_dict(row) if row else None


def get_user_by_email(email, include_password=False):
    ensure_db_ready()

    conn = get_db_connection()
    cur = conn.cursor()

    if include_password:
        cur.execute(
            """
            SELECT id, name, email, password_hash, role, created_at, updated_at
            FROM users
            WHERE LOWER(email) = LOWER(%s);
            """,
            (email,),
        )
        row = cur.fetchone()
        cur.close()
        conn.close()
        return _row_to_auth_dict(row) if row else None

    cur.execute(
        """
        SELECT id, name, email, role, created_at, updated_at
        FROM users
        WHERE LOWER(email) = LOWER(%s);
        """,
        (email,),
    )
    row = cur.fetchone()

    cur.close()
    conn.close()

    return _row_to_dict(row) if row else None


def add_user_to_db(name, email, password_hash=None, role="user"):
    ensure_db_ready()

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO users (name, email, password_hash, role)
        VALUES (%s, %s, %s, %s)
        RETURNING id, name, email, role, created_at, updated_at;
        """,
        (name, email, password_hash, role),
    )
    user = _row_to_dict(cur.fetchone())

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
        SET name = %s,
            email = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        RETURNING id, name, email, role, created_at, updated_at;
        """,
        (name, email, user_id),
    )
    row = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()

    return _row_to_dict(row) if row else None


def delete_user_from_db(user_id):
    ensure_db_ready()

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM users WHERE id = %s RETURNING id;", (user_id,))
    deleted = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()

    return deleted