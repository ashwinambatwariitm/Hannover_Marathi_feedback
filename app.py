import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
from collections import Counter
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")

DB_PATH = "feedback.db"

# -------------------------------
# Initialize database
# -------------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            overall TEXT,
            program TEXT,
            food TEXT,
            management TEXT,
            venue TEXT,
            favorite TEXT,
            suggestions TEXT,
            contribute TEXT,
            comments TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# -------------------------------
# Feedback Form
# -------------------------------
@app.route("/", methods=["GET"])
def home():
    return render_template("feedback.html")

# -------------------------------
# Submit Feedback
# -------------------------------
@app.route("/submit", methods=["POST"])
def submit():
    data = (
        request.form.get("overall_experience", ""),
        request.form.get("program_content", ""),
        request.form.get("food", ""),
        request.form.get("management", ""),
        request.form.get("venue", ""),
        request.form.get("favorite_part", ""),
        request.form.get("suggestions", ""),
        request.form.get("volunteer", ""),
        request.form.get("comments", ""),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO feedback 
        (overall, program, food, management, venue, favorite, suggestions, contribute, comments, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)
    conn.commit()
    conn.close()

    return redirect(url_for("thank_you"))

# -------------------------------
# Thank You Page
# -------------------------------
@app.route("/thankyou")
def thank_you():
    return render_template("thanks.html")

# -------------------------------
# Admin Login Page
# -------------------------------
@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password")
        if password == os.getenv("ADMIN_PASSWORD"):
            session["admin"] = True
            return redirect(url_for("dashboard"))
        else:
            return render_template("admin.html", error="Invalid password")
    return render_template("admin.html")

# -------------------------------
# Admin Dashboard
# -------------------------------
@app.route("/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM feedback ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()

    total_feedback = len(rows)

    # Count responses for charts
    overall = Counter(r[1] for r in rows)
    program = Counter(r[2] for r in rows)
    food = Counter(r[3] for r in rows)
    management = Counter(r[4] for r in rows)
    venue = Counter(r[5] for r in rows)
    contribute = Counter(r[8] for r in rows)

    return render_template(
        "admin_view.html",
        rows=rows,
        total_feedback=total_feedback,
        overall=overall,
        program=program,
        food=food,
        management=management,
        venue=venue,
        contribute=contribute
    )

# -------------------------------
# Admin Logout
# -------------------------------
@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("admin_login"))

# -------------------------------
# Run Flask App
# -------------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, port=port)
