import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
from backend import smart_clean_df, encode_column, perform_prediction, edit_dataframe

st.set_page_config(page_title="Graphico Backend", layout="centered")

st.title("🔐 Graphico Pro Backend")
st.caption("Secure computation layer for graphico.streamlit.app")

# ------------------- Simple API Key Protection -------------------
if "authorized" not in st.session_state:
    api_key = st.text_input("Enter Backend API Key", type="password", key="api_input")
    if st.button("Login to Backend"):
        if api_key == st.secrets.get("BACKEND_API_KEY", "dev-key-change-me"):
            st.session_state.authorized = True
            st.success("✅ Access Granted")
            st.rerun()
        else:
            st.error("❌ Invalid Key")
    st.stop()

st.success("🔓 Backend Ready")

# ------------------- Core Endpoints -------------------
st.subheader("Available Operations")

col1, col2 = st.columns(2)

with col1:
    if st.button("🧹 Clean Dataset", use_container_width=True):
        st.session_state.task = "clean"

with col2:
    if st.button("🧠 ML Prediction", use_container_width=True):
        st.session_state.task = "predict"

if st.session_state.get("task") == "clean":
    uploaded = st.file_uploader("Upload file for cleaning", type=["csv", "xlsx", "parquet"])
    if uploaded:
        try:
            if uploaded.name.endswith('.csv'):
                df = pd.read_csv(uploaded)
            else:
                df = pd.read_excel(uploaded)
            
            cleaned = smart_clean_df(df)
            st.dataframe(cleaned.head(100))
            
            # Download cleaned version
            csv = cleaned.to_csv(index=False).encode()
            st.download_button("Download Cleaned CSV", csv, "cleaned_data.csv")
            
        except Exception as e:
            st.error(f"Error: {e}")

elif st.session_state.get("task") == "predict":
    st.info("Prediction endpoint - extend with JSON payload from frontend later")
    # You can expand this later

st.divider()
st.caption("Connected to Google Sheet DB via service account")