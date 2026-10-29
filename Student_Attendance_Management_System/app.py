import csv
import io
import os
from flask import Flask, flash, redirect, render_template, request, Response, url_for
from database import init_db, get_db
from models import attendance_percentage, get_summary, low_attendance_students

def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-me"),
        DATABASE=os.environ.get("DATABASE_PATH", "attendance.db"),
        LOW_ATTENDANCE_THRESHOLD=float(os.environ.get("LOW_ATTENDANCE_THRESHOLD", "75")),
    )
    if test_config:
        app.config.update(test_config)

    init_db(app)

    @app.route("/")
    def dashboard():
        db = get_db()
        students = db.execute("SELECT * FROM students ORDER BY roll_number").fetchall()
        summary = get_summary(db, app.config["LOW_ATTENDANCE_THRESHOLD"])
        return render_template("dashboard.html", students=students, summary=summary)

    @app.route("/students", methods=["GET", "POST"])
    def students():
        db = get_db()
        if request.method == "POST":
            roll = request.form.get("roll_number", "").strip()
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip()
            if not roll or not name:
                flash("Roll number and name are required.", "error")
            else:
                try:
                    db.execute(
                        "INSERT INTO students (roll_number, name, email) VALUES (?, ?, ?)",
                        (roll, name, email),
                    )
                    db.commit()
                    flash("Student added successfully.", "success")
                    return redirect(url_for("students"))
                except Exception:
                    db.rollback()
                    flash("Could not add student. Check that the roll number is unique.", "error")
        rows = db.execute("SELECT * FROM students ORDER BY roll_number").fetchall()
        return render_template("students.html", students=rows)

    @app.route("/attendance", methods=["GET", "POST"])
    def attendance():
        db = get_db()
        students = db.execute("SELECT * FROM students ORDER BY roll_number").fetchall()
        if request.method == "POST":
            date = request.form.get("date", "").strip()
            if not date:
                flash("Please choose a date.", "error")
                return redirect(url_for("attendance"))
            for student in students:
                status = request.form.get(f"status_{student['id']}", "unmarked")
                if status not in {"present", "absent", "late", "excused"}:
                    continue
                db.execute(
                    """INSERT INTO attendance (student_id, date, status)
                       VALUES (?, ?, ?)
                       ON CONFLICT(student_id, date) DO UPDATE SET status=excluded.status""",
                    (student["id"], date, status),
                )
            db.commit()
            flash("Attendance saved.", "success")
            return redirect(url_for("attendance"))
        return render_template("attendance.html", students=students)

    @app.route("/reports")
    def reports():
        db = get_db()
        rows = db.execute("""
            SELECT s.id, s.roll_number, s.name,
                   SUM(CASE WHEN a.status IN ('present','late') THEN 1 ELSE 0 END) AS attended,
                   COUNT(a.id) AS sessions
            FROM students s LEFT JOIN attendance a ON a.student_id=s.id
            GROUP BY s.id ORDER BY s.roll_number
        """).fetchall()
        report_rows = []
        for row in rows:
            attended = row["attended"] or 0
            sessions = row["sessions"] or 0
            report_rows.append({
                "roll_number": row["roll_number"], "name": row["name"],
                "attended": attended, "sessions": sessions,
                "percentage": attendance_percentage(attended, sessions)
            })
        return render_template("reports.html", rows=report_rows)

    @app.route("/reports.csv")
    def export_csv():
        db = get_db()
        rows = db.execute("""
            SELECT s.roll_number, s.name,
                   SUM(CASE WHEN a.status IN ('present','late') THEN 1 ELSE 0 END) AS attended,
                   COUNT(a.id) AS sessions
            FROM students s LEFT JOIN attendance a ON a.student_id=s.id
            GROUP BY s.id ORDER BY s.roll_number
        """).fetchall()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Roll Number", "Student Name", "Attended Sessions", "Recorded Sessions", "Attendance %"])
        for row in rows:
            attended = row["attended"] or 0
            sessions = row["sessions"] or 0
            writer.writerow([row["roll_number"], row["name"], attended, sessions,
                             f"{attendance_percentage(attended, sessions):.2f}"])
        return Response(output.getvalue(), mimetype="text/csv",
                        headers={"Content-Disposition": "attachment; filename=attendance_report.csv"})

    @app.teardown_appcontext
    def close_db(exception=None):
        from database import close_db
        close_db(exception)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=os.environ.get("FLASK_DEBUG", "0") == "1")
