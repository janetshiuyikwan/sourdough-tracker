import streamlit as st
import sqlite3, os, pandas as pd
from datetime import datetime, date, time
from pathlib import Path

DB_NAME = "sourdough_starter.db"
UPLOAD_DIR = "starter_photos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_starters():
    try:
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql_query("SELECT * FROM starters ORDER BY name", conn); conn.close(); return df
    except: return pd.DataFrame()

def save_photo(f):
    if not f: return None
    p = Path(UPLOAD_DIR) / f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{f.name}"
    p.write_bytes(f.getbuffer()); return str(p)

st.title("➕ Add Feeding")
sp = get_starters()
if sp.empty:
    st.warning("Create a starter profile first in 🧫 Starter Profiles.")
else:
    opts = {r["name"]: int(r["id"]) for _, r in sp.iterrows()}
    with st.form("feed_form"):
        sel = st.selectbox("Starter", list(opts.keys()))
        d = st.date_input("Date", value=date.today())
        tm = st.time_input("Time", value=datetime.now().time())
        c1,c2,c3 = st.columns(3)
        with c1: sa = st.number_input("Starter (g)", min_value=0.0, step=1.0)
        with c2: fa = st.number_input("Flour (g)", min_value=0.0, step=1.0)
        with c3: wa = st.number_input("Water (g)", min_value=0.0, step=1.0)
        ratio = st.text_input("Ratio", value="1:1:1")
        ftype = st.selectbox("Flour type", ["White","Whole wheat","Rye","Mixed","Other"])
        temp = st.text_input("Temperature / environment")
        obs = st.text_area("Observation")
        st.markdown("### Health indicators (1=poor, 5=excellent)")
        rise = st.slider("Rise", 1, 5, 3)
        bubbles = st.slider("Bubbles", 1, 5, 3)
        aroma = st.slider("Aroma", 1, 5, 3)
        texture = st.slider("Texture", 1, 5, 3)
        reminder = st.time_input("Reminder time", value=time(8,0))
        photo = st.file_uploader("Upload photo", type=["jpg","jpeg","png"])
        if st.form_submit_button("💾 Save feeding"):
            hyd = round((wa/fa)*100,1) if fa > 0 else 0
            score = round((rise+bubbles+aroma+texture)/4*20,1)
            path = save_photo(photo)
            conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
            cur.execute("""INSERT INTO feedings (starter_id,feeding_date,feeding_time,starter_amount,flour_amount,water_amount,ratio,hydration,observation,flour_type,temperature,rise_level,bubbles_level,aroma_level,texture_level,health_score,reminder_time,photo_path,created_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (opts[sel],d.isoformat(),tm.strftime("%H:%M:%S"),sa,fa,wa,ratio,hyd,obs,ftype,temp,rise,bubbles,aroma,texture,score,
                 reminder.strftime("%H:%M:%S") if reminder else None, path, datetime.now().isoformat(timespec="seconds")))
            conn.commit(); conn.close()
            st.success(f"✅ Saved! Hydration: {hyd}% | Health score: {score}/100")
