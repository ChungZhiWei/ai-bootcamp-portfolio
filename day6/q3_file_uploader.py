import streamlit as st

resume = st.file_uploader("upload your resume", ["pdf", "txt"])
if resume:
    st.success(f"recieved: {resume.name}")
