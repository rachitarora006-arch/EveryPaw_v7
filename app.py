from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3
import os
import tempfile
from openpyxl import Workbook

app = Flask(__name__)
app.secret_key = "supersecretkey123"

# -----------------------------
# Admin credentials
# -----------------------------
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"

# -----------------------------
# Database Path
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')


# -----------------------------
# Initialize DB
# -----------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS reports(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT,
            animal TEXT,
            description TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS volunteers(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            city TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()


# -----------------------------
# Public Routes
# -----------------------------
@app.route('/')
def home():
    return render_template("index.html")


@app.route('/report', methods=['GET', 'POST'])
def report():
    if request.method == "POST":
        location = request.form['location']
        animal = request.form['animal']
        description = request.form['description']

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO reports (location, animal, description) VALUES (?, ?, ?)",
            (location, animal, description)
        )
        conn.commit()
        conn.close()
        return redirect('/')
    return render_template("report.html")


@app.route('/volunteer', methods=['GET', 'POST'])
def volunteer():
    if request.method == "POST":
        name = request.form['name']
        phone = request.form['phone']
        city = request.form['city']

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO volunteers (name, phone, city) VALUES (?, ?, ?)",
            (name, phone, city)
        )
        conn.commit()
        conn.close()
        return redirect('/')
    return render_template("volunteer.html")


@app.route('/map')
def map():
    return render_template("map.html")


@app.route('/learn')
def learn():
    return render_template("learn.html")


@app.route('/contact')
def contact():
    return render_template("contact.html")


@app.route('/about')
def about():
    return render_template("about.html")


# -----------------------------
# ADMIN LOGIN
# -----------------------------
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect('/admin-dashboard')
        return "Invalid credentials"
    return render_template("admin_login.html")


@app.route('/admin-dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect('/admin')
    return render_template("admin_dashboard.html")


@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/')


# -----------------------------
# PROTECTED ADMIN PAGES
# -----------------------------
@app.route('/view-reports')
def view_reports():
    if 'admin' not in session:
        return redirect('/admin')

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM reports")
    rows = c.fetchall()
    conn.close()
    return render_template("view_reports.html", reports=rows)


@app.route('/view-volunteers')
def view_volunteers():
    if 'admin' not in session:
        return redirect('/admin')

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM volunteers")
    rows = c.fetchall()
    conn.close()
    return render_template("view_volunteers.html", volunteers=rows)


# -----------------------------
# EXPORT TO EXCEL
# -----------------------------
@app.route('/export-volunteers')
def export_volunteers():
    if 'admin' not in session:
        return redirect('/admin')

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, name, phone, city FROM volunteers")
    rows = c.fetchall()
    conn.close()

    wb = Workbook()
    ws = wb.active
    ws.title = "Volunteers"
    ws.append(["ID", "Name", "Phone", "City"])

    for row in rows:
        ws.append(row)

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    wb.save(temp.name)

    return send_file(temp.name, as_attachment=True, download_name="volunteers.xlsx")


# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
