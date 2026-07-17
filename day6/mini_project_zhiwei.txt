import streamlit as st

st.sidebar.title("your info")
name = st.sidebar.text_input("name")

st.title("simple resume app")

if "upload_count" not in st.session_state:
    st.session_state.upload_count = 0
if "last_file_id" not in st.session_state:
    st.session_state.last_file_id = None

resume = st.file_uploader("upload your resume", type=["pdf", "txt"])
if resume:
    if resume.file_id != st.session_state.last_file_id:
        st.session_state.upload_count += 1
        st.session_state.last_file_id = resume.file_id
    st.success(f"hello {name}, we recieved: {resume.name}")

st.metric("times uploaded this session", st.session_state.upload_count)
