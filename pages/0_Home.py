import streamlit as st
import sqlite3, pandas as pd
from datetime import datetime

DB_NAME = "sourdough_starter.db"

def get_history():
    try:
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql_query(
            "SELECT f.*, s.name AS starter_name FROM feedings f JOIN starters s ON f.starter_id=s.id ORDER BY f.feeding_date DESC, f.feeding_time DESC",
            conn); conn.close()
        if not df.empty:
            df["feeding_date"] = pd.to_datetime(df["feeding_date"])
        return df
    except: return pd.DataFrame()

def due_warning(df):
    if df.empty: return None
    row = df.sort_values("feeding_date").iloc[-1]
    if not row.get("reminder_time") or pd.isna(row.get("reminder_time")): return None
    try:
        reminder = pd.to_datetime(str(row["feeding_date"].date()) + " " + str(row["reminder_time"]))
        diff = int((reminder - pd.Timestamp.now()).total_seconds() / 60)
        if 0 <= diff <= 60: return f"⏰ Feeding due in {diff} minutes!"
        if -60 <= diff < 0: return "⚠️ Feeding overdue by less than 1 hour!"
    except: pass
    return None

st.title("🏠 Home")
df = get_history()
warn = due_warning(df)
if warn: st.warning(warn)
if df.empty:
    st.info("No feedings yet. Go to Add Feeding to start.")
else:
    c1, c2, c3 = st.columns(3)
    c1.metric("Total feedings", len(df))
    c2.metric("Active starters", df["starter_name"].nunique())
    c3.metric("Avg health score", f"{df['health_score'].mean():.1f}/100" if "health_score" in df else "N/A")
    st.subheader("Latest feeding")
    latest = df.iloc[0]
    st.write(f"🧫 Starter: **{latest['starter_name']}**")
    st.write(f"📅 Date: {latest['feeding_date'].date()} {latest['feeding_time']}")
    st.write(f"💧 Hydration: {latest['hydration']}%")
    st.write(f"❤️ Health score: {latest['health_score']}/100")
    if latest.get("reminder_time"):
        st.write(f"⏰ Reminder set: {latest['reminder_time']}")
