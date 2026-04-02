from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret123"

DB = "database.db"


def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        password TEXT
    )
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        status INTEGER DEFAULT 0
    )
    """)
    conn.commit()
    conn.close()


@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect(DB)
    tasks = conn.execute("SELECT * FROM tasks").fetchall()

    total = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    completed = conn.execute("SELECT COUNT(*) FROM tasks WHERE status=1").fetchone()[0]
    pending = total - completed

    conn.close()

    return render_template("index.html",
                           tasks=tasks,
                           total=total,
                           completed=completed,
                           pending=pending)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect(DB)
        conn.execute("INSERT INTO users (email,password) VALUES (?,?)",
                     (email, password))
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect(DB)
        user = conn.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        ).fetchone()

        conn.close()

        if user:
            session["user"] = email
            return redirect("/")
        else:
            return "Login Failed"

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


@app.route("/add", methods=["POST"])
def add():
    title = request.form["title"]

    conn = sqlite3.connect(DB)
    conn.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect(DB)
    conn.execute("DELETE FROM tasks WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/complete/<int:id>")
def complete(id):
    conn = sqlite3.connect(DB)
    conn.execute("UPDATE tasks SET status=1 WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
