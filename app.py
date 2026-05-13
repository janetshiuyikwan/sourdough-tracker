import streamlit as st
import sqlite3, os

DB_NAME = "sourdough_starter.db"
UPLOAD_DIR = "starter_photos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS starters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        notes TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS feedings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        starter_id INTEGER NOT NULL,
        feeding_date TEXT NOT NULL,
        feeding_time TEXT NOT NULL,
        starter_amount REAL NOT NULL,
        flour_amount REAL NOT NULL,
        water_amount REAL NOT NULL,
        ratio TEXT, hydration REAL,
        observation TEXT, flour_type TEXT, temperature TEXT,
        rise_level INTEGER, bubbles_level INTEGER, aroma_level INTEGER, texture_level INTEGER,
        health_score REAL, reminder_time TEXT, photo_path TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (starter_id) REFERENCES starters (id))""")
    conn.commit(); conn.close()

init_db()
st.set_page_config(page_title="Sourdough Starter Tracker", page_icon="🍞", layout="wide")
st.title("🍞 Sourdough Starter Tracker")
st.markdown("""
Use the **sidebar** to navigate:
| Page | What it does |
|---|---|
| 🏠 Home | Overview, reminders, quick stats |
| ➕ Add Feeding | Log a new feeding |
| 📋 History | View, edit, delete, export CSV |
| 🧫 Starter Profiles | Manage your starters |
""")
st.divider()
st.caption("Data saved in sourdough_starter.db | Photos in starter_photos/")
