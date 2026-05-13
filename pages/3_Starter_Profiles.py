import streamlit as st
import sqlite3, pandas as pd

DB_NAME = "sourdough_starter.db"

def get_starters():
    try:
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql_query("SELECT * FROM starters ORDER BY name", conn); conn.close(); return df
    except: return pd.DataFrame()

st.title("🧫 Starter Profiles")
with st.form("add_form"):
    name = st.text_input("New starter name")
    notes = st.text_area("Notes")
    if st.form_submit_button("➕ Add starter"):
        if name.strip():
            conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
            cur.execute("INSERT OR IGNORE INTO starters (name, notes) VALUES (?,?)", (name.strip(), notes.strip()))
            conn.commit(); conn.close(); st.rerun()
        else: st.error("Name cannot be empty.")

df = get_starters()
if df.empty:
    st.info("No starters yet.")
else:
    st.dataframe(df, use_container_width=True)
    pick = st.selectbox("Edit / delete starter", df["name"].tolist())
    row = df[df["name"]==pick].iloc[0]
    with st.form("edit_form"):
        n2 = st.text_input("Name", value=row["name"])
        nt2 = st.text_area("Notes", value=row["notes"] or "")
        c1,c2 = st.columns(2)
        with c1:
            if st.form_submit_button("💾 Save"):
                conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
                cur.execute("UPDATE starters SET name=?, notes=? WHERE id=?", (n2.strip(), nt2.strip(), int(row["id"])))
                conn.commit(); conn.close(); st.rerun()
        with c2:
            if st.form_submit_button("🗑️ Delete"):
                conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
                cur.execute("DELETE FROM feedings WHERE starter_id=?", (int(row["id"]),))
                cur.execute("DELETE FROM starters WHERE id=?", (int(row["id"]),))
                conn.commit(); conn.close(); st.rerun()
