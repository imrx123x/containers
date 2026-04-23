from app.db import get_db_connection


def _row_to_dict(row):
    return {
        "id": row[0],
        "name": row[1],
        "email": row[2],
        "role": row[3],
        "created_at": row[4],
        "updated_at": row[5],
        "deleted_at": row[6],
        "token_version": row[7],
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
        "deleted_at": row[7],
        "token_version": row[8],
    }


def get_users_paginated(page: int, limit: int):
    offset = (page - 1) * limit

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, name, email, role, created_at, updated_at, deleted_at, token_version
        FROM users
        WHERE deleted_at IS NULL
        ORDER BY id
        LIMIT %s OFFSET %s;
        """,
        (limit, offset),
    )
    users = [_row_to_dict(row) for row in cur.fetchall()]

    cur.execute(
        """
        SELECT COUNT(*)
        FROM users
        WHERE deleted_at IS NULL;
        """
    )
    total = cur.fetchone()[0]

    cur.close()
    conn.close()

    return users, total


def get_deleted_users_paginated(page: int, limit: int):
    offset = (page - 1) * limit

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, name, email, role, created_at, updated_at, deleted_at, token_version
        FROM users
        WHERE deleted_at IS NOT NULL
        ORDER BY deleted_at DESC, id DESC
        LIMIT %s OFFSET %s;
        """,
        (limit, offset),
    )
    users = [_row_to_dict(row) for row in cur.fetchall()]

    cur.execute(
        """
        SELECT COUNT(*)
        FROM users
        WHERE deleted_at IS NOT NULL;
        """
    )
    total = cur.fetchone()[0]

    cur.close()
    conn.close()

    return users, total


def search_users_paginated(query: str, page: int, limit: int):
    offset = (page - 1) * limit
    like_query = f"%{query.lower()}%"

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, name, email, role, created_at, updated_at, deleted_at, token_version
        FROM users
        WHERE deleted_at IS NULL
          AND (
                LOWER(name) LIKE %s
                OR LOWER(COALESCE(email, '')) LIKE %s
          )
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
        WHERE deleted_at IS NULL
          AND (
                LOWER(name) LIKE %s
                OR LOWER(COALESCE(email, '')) LIKE %s
          );
        """,
        (like_query, like_query),
    )
    total = cur.fetchone()[0]

    cur.close()
    conn.close()

    return users, total


def get_user_by_id(user_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, name, email, role, created_at, updated_at, deleted_at, token_version
        FROM users
        WHERE id = %s
          AND deleted_at IS NULL;
        """,
        (user_id,),
    )
    row = cur.fetchone()

    cur.close()
    conn.close()

    return _row_to_dict(row) if row else None


def get_user_by_email(email, include_password=False):
    conn = get_db_connection()
    cur = conn.cursor()

    if include_password:
        cur.execute(
            """
            SELECT id, name, email, password_hash, role, created_at, updated_at, deleted_at, token_version
            FROM users
            WHERE LOWER(email) = LOWER(%s)
              AND deleted_at IS NULL;
            """,
            (email,),
        )
        row = cur.fetchone()
        cur.close()
        conn.close()
        return _row_to_auth_dict(row) if row else None

    cur.execute(
        """
        SELECT id, name, email, role, created_at, updated_at, deleted_at, token_version
        FROM users
        WHERE LOWER(email) = LOWER(%s)
          AND deleted_at IS NULL;
        """,
        (email,),
    )
    row = cur.fetchone()

    cur.close()
    conn.close()

    return _row_to_dict(row) if row else None


def add_user_to_db(name, email, password_hash=None, role="user"):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO users (name, email, password_hash, role)
        VALUES (%s, %s, %s, %s)
        RETURNING id, name, email, role, created_at, updated_at, deleted_at, token_version;
        """,
        (name, email, password_hash, role),
    )
    user = _row_to_dict(cur.fetchone())

    conn.commit()
    cur.close()
    conn.close()

    return user


def update_user_in_db(user_id, name, email):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE users
        SET name = %s,
            email = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
          AND deleted_at IS NULL
        RETURNING id, name, email, role, created_at, updated_at, deleted_at, token_version;
        """,
        (name, email, user_id),
    )
    row = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()

    return _row_to_dict(row) if row else None


def update_user_password_in_db(user_id, password_hash):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE users
        SET password_hash = %s,
            token_version = token_version + 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
          AND deleted_at IS NULL
        RETURNING id, name, email, role, created_at, updated_at, deleted_at, token_version;
        """,
        (password_hash, user_id),
    )
    row = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()

    return _row_to_dict(row) if row else None


def soft_delete_user_from_db(user_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE users
        SET deleted_at = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
          AND deleted_at IS NULL
        RETURNING id, name, email, role, created_at, updated_at, deleted_at, token_version;
        """,
        (user_id,),
    )
    row = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()

    return _row_to_dict(row) if row else None


def restore_user_in_db(user_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE users
        SET deleted_at = NULL,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
          AND deleted_at IS NOT NULL
        RETURNING id, name, email, role, created_at, updated_at, deleted_at, token_version;
        """,
        (user_id,),
    )
    row = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()

    return _row_to_dict(row) if row else None


def hard_delete_user_from_db(user_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        DELETE FROM users
        WHERE id = %s
          AND deleted_at IS NOT NULL
        RETURNING id, name, email, role, created_at, updated_at, deleted_at, token_version;
        """,
        (user_id,),
    )
    row = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()

    return _row_to_dict(row) if row else None


def get_dashboard_stats():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM users WHERE deleted_at IS NULL;")
    total_users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM users WHERE role = 'admin' AND deleted_at IS NULL;")
    total_admins = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM users WHERE role = 'user' AND deleted_at IS NULL;")
    total_regular_users = cur.fetchone()[0]

    cur.execute(
        """
        SELECT id, name, email, role, created_at, updated_at, deleted_at, token_version
        FROM users
        WHERE deleted_at IS NULL
        ORDER BY id DESC
        LIMIT 1;
        """
    )
    latest_user_row = cur.fetchone()

    cur.close()
    conn.close()

    latest_user = _row_to_dict(latest_user_row) if latest_user_row else None

    return {
        "total_users": total_users,
        "total_admins": total_admins,
        "total_regular_users": total_regular_users,
        "latest_user": latest_user,
    }


def add_audit_log(
    action,
    actor_id=None,
    actor_email=None,
    target_user_id=None,
    target_email=None,
    details=None,
):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO audit_logs (
            action,
            actor_id,
            actor_email,
            target_user_id,
            target_email,
            details
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id, action, actor_id, actor_email, target_user_id, target_email, details, created_at;
        """,
        (
            action,
            actor_id,
            actor_email,
            target_user_id,
            target_email,
            details,
        ),
    )
    row = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()

    return {
        "id": row[0],
        "action": row[1],
        "actor_id": row[2],
        "actor_email": row[3],
        "target_user_id": row[4],
        "target_email": row[5],
        "details": row[6],
        "created_at": row[7],
    }


def get_recent_audit_logs(limit: int = 10):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, action, actor_id, actor_email, target_user_id, target_email, details, created_at
        FROM audit_logs
        ORDER BY id DESC
        LIMIT %s;
        """,
        (limit,),
    )
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "id": row[0],
            "action": row[1],
            "actor_id": row[2],
            "actor_email": row[3],
            "target_user_id": row[4],
            "target_email": row[5],
            "details": row[6],
            "created_at": row[7],
        }
        for row in rows
    ]


def delete_user_from_db(user_id):
    return soft_delete_user_from_db(user_id)