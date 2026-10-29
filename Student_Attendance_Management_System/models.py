def attendance_percentage(attended, sessions):
    """Return attendance percentage; avoid division by zero."""
    if sessions <= 0:
        return 0.0
    return (attended / sessions) * 100.0

def get_summary(db, threshold=75.0):
    total = db.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    present_today = db.execute(
        "SELECT COUNT(DISTINCT student_id) FROM attendance WHERE date = date('now') AND status IN ('present','late')"
    ).fetchone()[0]
    low = low_attendance_students(db, threshold)
    return {"total_students": total, "present_today": present_today, "low_attendance": len(low)}

def low_attendance_students(db, threshold=75.0):
    rows = db.execute("""
        SELECT s.id, s.roll_number, s.name,
               SUM(CASE WHEN a.status IN ('present','late') THEN 1 ELSE 0 END) AS attended,
               COUNT(a.id) AS sessions
        FROM students s LEFT JOIN attendance a ON a.student_id=s.id
        GROUP BY s.id ORDER BY s.roll_number
    """).fetchall()
    result = []
    for row in rows:
        sessions = row["sessions"] or 0
        attended = row["attended"] or 0
        percentage = attendance_percentage(attended, sessions)
        if sessions > 0 and percentage < threshold:
            result.append({"roll_number": row["roll_number"], "name": row["name"],
                           "attended": attended, "sessions": sessions, "percentage": percentage})
    return result
