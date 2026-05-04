import os

import requests
import streamlit as st

DEFAULT_API_URL = "https://web-production-d6ffa.up.railway.app"
API = os.getenv("API_URL", st.secrets.get("API_URL", DEFAULT_API_URL)).rstrip("/")

st.set_page_config(page_title="External Business Intel", layout="wide")

st.title("External Business Intelligence Console")
st.caption(f"API target: {API}")

mode = st.sidebar.radio("Mode", ["Scan", "Latest", "History", "System Health"])


def call(endpoint, params=None, timeout=60):
    try:
        r = requests.get(f"{API}{endpoint}", params=params, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP error: {e}")
        try:
            st.code(r.text)
        except Exception:
            pass
        return None
    except Exception as e:
        st.error(f"Request failed: {e}")
        return None


def render_trends(data):
    analysis = data.get("analysis", {}) if data else {}
    trends = analysis.get("trends", [])
    if not trends:
        st.warning("No trends detected")
        return

    for t in trends:
        with st.container(border=True):
            left, right = st.columns([2, 1])
            with left:
                st.subheader(t.get("trend", "Unnamed trend"))
                st.write(f"**Implication:** {t.get('implication', 'Not provided')}")
                st.write(f"**Action:** {t.get('recommended_action', 'Not provided')}")
            with right:
                st.metric("Strength", t.get("strength", "unknown"))
                if t.get("confidence"):
                    st.metric("Confidence", t.get("confidence"))
                if t.get("score") is not None:
                    st.metric("Score", t.get("score"))

            with st.expander("Evidence"):
                evidence = t.get("evidence", [])
                if not evidence:
                    st.write("No evidence returned")
                for e in evidence:
                    st.markdown(f"- **{e.get('source', 'source')}**: {e.get('excerpt', '')}")
                    if e.get("source_url"):
                        st.caption(e.get("source_url"))


def render_report_item(item):
    st.write(f"**Query:** {item.get('query')}")
    st.write(f"**Created:** {item.get('created_at')}")
    render_trends({"analysis": item.get("report", {})})


if mode == "Scan":
    st.header("Run On-Demand Scan")
    q = st.text_input("Query", "marketing")
    if st.button("Run Scan", type="primary"):
        with st.spinner("Running public-domain scan, ETL, analysis, and storage..."):
            data = call("/trends/scan", {"query": q}, timeout=90)
        if data:
            st.success(f"Processed {data.get('records_processed')} records | Stored: {data.get('stored')}")
            render_trends(data)
            with st.expander("Raw response"):
                st.json(data)

elif mode == "Latest":
    st.header("Latest Stored Report")
    q = st.text_input("Filter query (optional)", "")
    data = call("/trends/latest", {"query": q} if q else None)
    if data:
        if data.get("found"):
            render_report_item(data.get("item", {}))
        else:
            st.info("No stored report found")

elif mode == "History":
    st.header("Report History")
    q = st.text_input("Filter query (optional)", "")
    limit = st.slider("Limit", 1, 100, 20)
    data = call("/trends/history", {"query": q, "limit": limit} if q else {"limit": limit})
    if data:
        st.write(f"Reports returned: {data.get('count')}")
        for item in data.get("items", []):
            with st.expander(f"{item.get('query')} | {item.get('created_at')}"):
                render_report_item(item)

elif mode == "System Health":
    st.header("System Health")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Runtime")
        health = call("/health")
        st.json(health)
    with col2:
        st.subheader("Database Smoke")
        smoke = call("/admin/smoke")
        st.json(smoke)
