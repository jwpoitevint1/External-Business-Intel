import streamlit as st
import requests

API = st.secrets.get("API_URL", "https://web-production-d6ffa.up.railway.app")

st.set_page_config(page_title="External Business Intel", layout="wide")

st.title("External Business Intelligence Console")

mode = st.sidebar.radio("Mode", ["Scan", "Latest", "History", "System Health"])


def call(endpoint, params=None):
    try:
        r = requests.get(f"{API}{endpoint}", params=params, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(str(e))
        return None


def render_trends(data):
    trends = data.get("analysis", {}).get("trends", [])
    if not trends:
        st.warning("No trends detected")
        return

    for t in trends:
        with st.container():
            st.subheader(t.get("trend"))
            st.write(f"Strength: {t.get('strength')}")
            st.write(f"Implication: {t.get('implication')}")
            st.write(f"Action: {t.get('recommended_action')}")
            with st.expander("Evidence"):
                for e in t.get("evidence", []):
                    st.write(e.get("excerpt"))


if mode == "Scan":
    q = st.text_input("Query", "marketing")
    if st.button("Run Scan"):
        data = call("/trends/scan", {"query": q})
        if data:
            st.success(f"Processed {data.get('records_processed')} records")
            render_trends(data)

elif mode == "Latest":
    data = call("/trends/latest")
    if data and data.get("found"):
        render_trends({"analysis": data["item"]["report"]})

elif mode == "History":
    data = call("/trends/history")
    if data:
        for item in data.get("items", []):
            with st.expander(f"{item['query']} | {item['created_at']}"):
                render_trends({"analysis": item["report"]})

elif mode == "System Health":
    health = call("/health")
    smoke = call("/admin/smoke")
    st.subheader("Health")
    st.json(health)
    st.subheader("System Smoke")
    st.json(smoke)
