import streamlit as st

uploaded_file = st.file_uploader("upload document", type = ["pdf","txt"])

if uploaded_file:
    st.success("file uploaded")
    st.write(f"file name: {uploaded_file.name}")
