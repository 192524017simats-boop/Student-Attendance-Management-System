import sqlite3
from models import attendance_percentage

def test_attendance_percentage_normal():
    assert attendance_percentage(3, 4) == 75.0

def test_attendance_percentage_zero_sessions():
    assert attendance_percentage(0, 0) == 0.0

def test_attendance_percentage_full_attendance():
    assert attendance_percentage(5, 5) == 100.0
