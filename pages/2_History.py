import streamlit as st
import sqlite3, pandas as pd, os
import plotly.express as px
from pathlib import Path

DB_NAME = "sourdough_starter.db"

def get_history():
    try:
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql_query(
            "SELECT f.*, s.name AS starter_name FROM feedings f JOIN starters s ON f.starter_id=s.id ORDER BY f.feeding_date DESC, f.feeding_time DESC",
            conn); conn.close()
        if not df.empty: df["feeding_date"] = pd.to_datetime(df["feeding_date"])
        return df
    except: return pd.DataFrame()

def delete_feeding(rid):
    conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
    cur.execute("DELETE FROM feedings WHERE id=?", (rid,)); conn.commit(); conn.close()

st.title("📋 History")
df = get_history()
if df.empty:
    st.info("No records yet.")
else:
    st.dataframe(df[["id","starter_name","feeding_date","feeding_time","hydration","health_score","observation","reminder_time"]], use_container_width=True)
    st.download_button("📥 Download CSV", df.to_csv(index=False).encode("utf-8"), "sourdough_feedings.csv", "text/csv")
    st.markdown("### Delete record")
    rid = st.selectbox("Select record ID", df["id"].tolist())
    row = df[df["id"]==rid].iloc[0]
    st.caption(f"Starter: {row['starter_name']} | Date: {row['feeding_date'].date()} | Score: {row['health_score']}/100")
    if row.get("photo_path") and os.path.exists(str(row["photo_path"])):
        st.image(str(row["photo_path"]), caption="Starter photo", width=250)
    if st.button("🗑️ Delete record"):
        delete_feeding(int(rid)); st.success("Deleted."); st.rerun()
    st.markdown("### 📅 Calendar view")
    by_day = df.groupby(df["feeding_date"].dt.date).size().reset_index(name="feedings")
    by_day.columns = ["date","feedings"]
    fig = px.bar(by_day, x="date", y="feedings", title="Feeding Frequency by Day")
    st.plotly_chart(fig, use_container_width=True)
    fig2 = px.line(df.sort_values("feeding_date"), x="feeding_date", y="health_score", color="starter_name", title="Health Score Over Time")
    st.plotly_chart(fig2, use_container_width=True)
