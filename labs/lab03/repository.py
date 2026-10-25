from contextlib import closing

from .database import get_connection


def get_categories():
    with closing(get_connection()) as conn:
        rows = conn.execute("SELECT id, name FROM categories ORDER BY id ASC").fetchall()
        return [{"id": r[0], "name": r[1]} for r in rows]

def create_category(name: str):
    with closing(get_connection()) as conn, conn:
        cur = conn.execute("INSERT INTO categories (name) VALUES (?)", (name,))
        return {"id": cur.lastrowid, "name": name}

def delete_category(category_id: int):
    with closing(get_connection()) as conn, conn:
        cur = conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        return cur.rowcount > 0

def get_record(record_id: int):
    query = """
        SELECT r.id, r.code, r.title, r.category_id, r.value, r.status, c.name 
        FROM records r 
        JOIN categories c ON r.category_id = c.id 
        WHERE r.id = ?
    """
    with closing(get_connection()) as conn:
        row = conn.execute(query, (record_id,)).fetchone()
        if row:
            return {
                "id": row[0], "code": row[1], "title": row[2], 
                "category_id": row[3], "value": row[4], "status": row[5], "category_name": row[6]
            }
        return None

def create_record(data: dict):
    query = "INSERT INTO records (code, title, category_id, value, status) VALUES (?, ?, ?, ?, ?)"
    with closing(get_connection()) as conn, conn:
        cur = conn.execute(query, (data["code"], data["title"], data["category_id"], data["value"], data["status"]))
        return get_record(cur.lastrowid)

def get_records(category_id: int | None, status: str | None, min_value: float | None, q: str | None, limit: int, offset: int):
    query = """
        SELECT r.id, r.code, r.title, r.category_id, r.value, r.status, c.name 
        FROM records r 
        JOIN categories c ON r.category_id = c.id 
        WHERE 1=1
    """
    params = []
    if category_id is not None:
        query += " AND r.category_id = ?"
        params.append(category_id)
    if status is not None:
        query += " AND r.status = ?"
        params.append(status)
    if min_value is not None:
        query += " AND r.value >= ?"
        params.append(min_value)
    if q is not None:
        query += " AND instr(r.title, ?) > 0"
        params.append(q)
    
    query += " ORDER BY r.id ASC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    with closing(get_connection()) as conn:
        rows = conn.execute(query, params).fetchall()
        return [
            {"id": row[0], "code": row[1], "title": row[2], "category_id": row[3], 
             "value": row[4], "status": row[5], "category_name": row[6]} 
            for row in rows
        ]

def update_record(record_id: int, data: dict):
    query = "UPDATE records SET code = ?, title = ?, category_id = ?, value = ?, status = ? WHERE id = ?"
    with closing(get_connection()) as conn, conn:
        cur = conn.execute(query, (data["code"], data["title"], data["category_id"], data["value"], data["status"], record_id))
        if cur.rowcount > 0:
            return get_record(record_id)
        return None

def delete_record(record_id: int):
    with closing(get_connection()) as conn, conn:
        cur = conn.execute("DELETE FROM records WHERE id = ?", (record_id,))
        return cur.rowcount > 0

def bulk_create_records(records_data: list[dict]):
    insert_query = "INSERT INTO records (code, title, category_id, value, status) VALUES (?, ?, ?, ?, ?)"
    params = [(d["code"], d["title"], d["category_id"], d["value"], d["status"]) for d in records_data]
    
    with closing(get_connection()) as conn, conn:
        conn.executemany(insert_query, params)
        
        codes = [d["code"] for d in records_data]
        placeholders = ",".join("?" * len(codes))
        select_query = f"""
            SELECT r.id, r.code, r.title, r.category_id, r.value, r.status, c.name 
            FROM records r 
            JOIN categories c ON r.category_id = c.id 
            WHERE r.code IN ({placeholders})
        """
        rows = conn.execute(select_query, codes).fetchall()
        return [
            {"id": row[0], "code": row[1], "title": row[2], "category_id": row[3], 
             "value": row[4], "status": row[5], "category_name": row[6]} 
            for row in rows
        ]