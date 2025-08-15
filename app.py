from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3, os, hashlib, json, hmac
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Change in production

DB_PATH = "quiz.db"

# ------------------------------
# Database helper
# ------------------------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT CHECK(role IN ('admin','user')) NOT NULL DEFAULT 'user',
        created_at TEXT NOT NULL
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS quizzes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        created_by INTEGER NOT NULL,
        created_at TEXT NOT NULL
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quiz_id INTEGER NOT NULL,
        question TEXT NOT NULL,
        option_a TEXT NOT NULL,
        option_b TEXT NOT NULL,
        option_c TEXT NOT NULL,
        option_d TEXT NOT NULL,
        correct_option CHAR(1) NOT NULL
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        quiz_id INTEGER NOT NULL,
        started_at TEXT NOT NULL,
        finished_at TEXT NOT NULL,
        total_questions INTEGER NOT NULL,
        score INTEGER NOT NULL,
        details_json TEXT NOT NULL
    )""")
    
    # Create admin user if not exists
    cur.execute("SELECT * FROM users WHERE username='admin'")
    if not cur.fetchone():
        cur.execute("INSERT INTO users (username, password_hash, role, created_at) VALUES (?,?,?,?)",
                    ("admin", hash_password("admin123"), "admin", datetime.utcnow().isoformat()))
    
    conn.commit()
    conn.close()

# ------------------------------
# Password helpers
# ------------------------------
def hash_password(password):
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return f"{salt.hex()}${dk.hex()}"

def verify_password(password, stored):
    try:
        salt_hex, hash_hex = stored.split("$")
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
        return hmac.compare_digest(dk, expected)
    except:
        return False

# ------------------------------
# Routes
# ------------------------------
@app.route("/")
def index():
    if "user" not in session:
        return redirect(url_for("login"))
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM quizzes")
    quizzes = cur.fetchall()
    conn.close()
    return render_template("index.html", quizzes=quizzes)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (username, password_hash, role, created_at) VALUES (?,?,?,?)",
                        (username, hash_password(password), "user", datetime.utcnow().isoformat()))
            conn.commit()
            flash("Registration successful! Please log in.")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username already exists.")
        finally:
            conn.close()
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        row = cur.fetchone()
        conn.close()
        if row and verify_password(password, row["password_hash"]):
            session["user"] = {"id": row["id"], "username": row["username"], "role": row["role"]}
            if row["role"] == "admin":
                return redirect(url_for("admin_dashboard"))
            else:
                return redirect(url_for("index"))
        flash("Invalid credentials.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out successfully.")
    return redirect(url_for("index"))

# ------------------------------
# Admin
# ------------------------------
@app.route("/admin")
def admin_dashboard():
    if "user" not in session or session["user"]["role"] != "admin":
        return redirect(url_for("login"))
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM quizzes")
    quizzes = cur.fetchall()
    conn.close()
    return render_template("admin_dashboard.html", quizzes=quizzes)

@app.route("/admin/create_quiz", methods=["GET", "POST"])
def create_quiz():
    if "user" not in session or session["user"]["role"] != "admin":
        return redirect(url_for("login"))
    if request.method == "POST":
        name = request.form["name"]
        category = request.form["category"]
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO quizzes (name, category, created_by, created_at) VALUES (?,?,?,?)",
                    (name, category, session["user"]["id"], datetime.utcnow().isoformat()))
        conn.commit()
        conn.close()
        flash("Quiz created successfully!")
        return redirect(url_for("admin_dashboard"))
    return render_template("create_quiz.html")

@app.route("/admin/add_question/<int:quiz_id>", methods=["GET", "POST"])
def add_question(quiz_id):
    if "user" not in session or session["user"]["role"] != "admin":
        return redirect(url_for("login"))
    if request.method == "POST":
        q = request.form["question"]
        a = request.form["option_a"]
        b = request.form["option_b"]
        c = request.form["option_c"]
        d = request.form["option_d"]
        correct = request.form["correct_option"]
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""INSERT INTO questions (quiz_id, question, option_a, option_b, option_c, option_d, correct_option)
                       VALUES (?,?,?,?,?,?,?)""", (quiz_id, q, a, b, c, d, correct))
        conn.commit()
        conn.close()
        flash("Question added successfully!")
        return redirect(url_for("admin_dashboard"))
    return render_template("add_question.html", quiz_id=quiz_id)

@app.route("/admin/view_questions/<int:quiz_id>")
def view_questions(quiz_id):
    if "user" not in session or session["user"]["role"] != "admin":
        return redirect(url_for("login"))
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM questions WHERE quiz_id=?", (quiz_id,))
    questions = cur.fetchall()
    cur.execute("SELECT name FROM quizzes WHERE id=?", (quiz_id,))
    quiz = cur.fetchone()
    conn.close()
    return render_template("view_questions.html", questions=questions, quiz=quiz)

@app.route("/admin/view_attempts")
def view_attempts():
    if "user" not in session or session["user"]["role"] != "admin":
        return redirect(url_for("login"))
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.*, u.username, q.name as quiz_name 
        FROM attempts a 
        JOIN users u ON a.user_id = u.id 
        JOIN quizzes q ON a.quiz_id = q.id 
        ORDER BY a.finished_at DESC
    """)
    attempts = cur.fetchall()
    conn.close()
    return render_template("view_attempts.html", attempts=attempts)

# ------------------------------
# User: Take quiz
# ------------------------------
@app.route("/take_quiz/<int:quiz_id>", methods=["GET", "POST"])
def take_quiz(quiz_id):
    if "user" not in session or session["user"]["role"] != "user":
        return redirect(url_for("login"))
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM questions WHERE quiz_id=?", (quiz_id,))
    questions = cur.fetchall()
    cur.execute("SELECT name FROM quizzes WHERE id=?", (quiz_id,))
    quiz = cur.fetchone()
    
    if request.method == "POST":
        score = 0
        details = []
        for q in questions:
            ans = request.form.get(str(q["id"]))
            if ans == q["correct_option"]:
                score += 4
            elif ans:
                score -= 1
            details.append({"qid": q["id"], "chosen": ans, "correct": q["correct_option"]})
        cur.execute("""INSERT INTO attempts (user_id, quiz_id, started_at, finished_at, total_questions, score, details_json)
                       VALUES (?,?,?,?,?,?,?)""",
                    (session["user"]["id"], quiz_id, datetime.utcnow().isoformat(), datetime.utcnow().isoformat(),
                     len(questions), score, json.dumps(details)))
        conn.commit()
        conn.close()
        return render_template("quiz_result.html", score=score, total=len(questions)*4, quiz_name=quiz["name"])
    conn.close()
    return render_template("take_quiz.html", questions=questions, quiz=quiz)

@app.route("/my_scores")
def my_scores():
    if "user" not in session:
        return redirect(url_for("login"))
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.*, q.name as quiz_name 
        FROM attempts a 
        JOIN quizzes q ON a.quiz_id = q.id 
        WHERE a.user_id = ? 
        ORDER BY a.finished_at DESC
    """, (session["user"]["id"],))
    attempts = cur.fetchall()
    conn.close()
    return render_template("my_scores.html", attempts=attempts)

if __name__ == "__main__":
    init_db()
    app.run(debug=True) 