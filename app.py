import os
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

DB_PATH = os.getenv("DB_PATH", "/data/todos.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed BOOLEAN NOT NULL DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200


@app.route("/todos", methods=["GET"])
def get_todos():
    conn = get_db()

    todos = conn.execute(
        "SELECT id, title, completed FROM todos ORDER BY id"
    ).fetchall()

    conn.close()

    return jsonify([dict(todo) for todo in todos])


@app.route("/todos", methods=["POST"])
def create_todo():
    data = request.get_json()

    if not data or "title" not in data:
        return jsonify({"error": "title is required"}), 400

    title = data["title"]
    completed = data.get("completed", False)

    conn = get_db()

    cursor = conn.execute(
        "INSERT INTO todos (title, completed) VALUES (?, ?)",
        (title, completed)
    )

    conn.commit()

    todo_id = cursor.lastrowid

    todo = conn.execute(
        "SELECT id, title, completed FROM todos WHERE id = ?",
        (todo_id,)
    ).fetchone()

    conn.close()

    return jsonify(dict(todo)), 201


@app.route("/todos/<int:todo_id>", methods=["GET"])
def get_todo(todo_id):
    conn = get_db()

    todo = conn.execute(
        "SELECT id, title, completed FROM todos WHERE id = ?",
        (todo_id,)
    ).fetchone()

    conn.close()

    if todo is None:
        return jsonify({"error": "todo not found"}), 404

    return jsonify(dict(todo))


@app.route("/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id):
    data = request.get_json()

    if not data:
        return jsonify({"error": "request body is required"}), 400

    conn = get_db()

    todo = conn.execute(
        "SELECT id, title, completed FROM todos WHERE id = ?",
        (todo_id,)
    ).fetchone()

    if todo is None:
        conn.close()
        return jsonify({"error": "todo not found"}), 404

    title = data.get("title", todo["title"])
    completed = data.get("completed", todo["completed"])

    conn.execute(
        """
        UPDATE todos
        SET title = ?, completed = ?
        WHERE id = ?
        """,
        (title, completed, todo_id)
    )

    conn.commit()

    updated_todo = conn.execute(
        "SELECT id, title, completed FROM todos WHERE id = ?",
        (todo_id,)
    ).fetchone()

    conn.close()

    return jsonify(dict(updated_todo))


@app.route("/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    conn = get_db()

    todo = conn.execute(
        "SELECT id FROM todos WHERE id = ?",
        (todo_id,)
    ).fetchone()

    if todo is None:
        conn.close()
        return jsonify({"error": "todo not found"}), 404

    conn.execute(
        "DELETE FROM todos WHERE id = ?",
        (todo_id,)
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "todo deleted"})


if __name__ == "__main__":
    init_db()

    app.run(
        host="0.0.0.0",
        port=3000
    )


    