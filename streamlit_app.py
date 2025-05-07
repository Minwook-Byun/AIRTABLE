# streamlit_app.py
import streamlit as st
import requests
import pandas as pd
from urllib.parse import quote

from dotenv import load_dotenv
import os

load_dotenv()

AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
BASE_ID = os.getenv("BASE_ID")
table_name = quote(os.getenv("TABLE_NAME"))  # 한글 테이블 이름 안전하게 인코딩

@st.cache_data
def fetch_airtable():
    url = f"https://api.airtable.com/v0/{BASE_ID}/{table_name}"
    headers = {"Authorization": f"Bearer {AIRTABLE_API_KEY}"}
    all_records = []
    offset = None

    while True:
        params = {"offset": offset} if offset else {}
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        all_records.extend(data.get("records", []))
        offset = data.get("offset")
        if not offset:
            break

    rows = []
    for r in all_records:
        f = r["fields"]
        rows.append({
            "이름": f.get("이름", "없음"),
            "투자 조건": f.get("투자 조건", "미정"),
            "기준금액": f.get("기준금액", 0),
        })
    return pd.DataFrame(rows)

# 👉 UI 시작
st.title("📊 Airtable 인터랙티브 피벗 대시보드")

df = fetch_airtable()

if df.empty:
    st.warning("Airtable에서 데이터를 불러오지 못했습니다.")
    st.stop()

# ✅ 조건 필터
conditions = df["투자 조건"].dropna().unique().tolist()
selected = st.multiselect("투자 조건 필터", conditions, default=conditions)

# 🔍 필터 적용
filtered_df = df[df["투자 조건"].isin(selected)]

# 🔁 피벗 테이블
pivot = filtered_df.pivot_table(index="이름", columns="투자 조건", values="기준금액", aggfunc="sum", fill_value=0)

# 🎨 강조 스타일 적용
styled = pivot.style.highlight_max(axis=1, color="#ffeeba")

# 📋 표시해야지 
st.dataframe(styled, use_container_width=True)
