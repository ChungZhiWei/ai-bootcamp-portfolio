import streamlit as st

st.sidebar.title("settings")
st.sidebar.markdown("please enter your details")
username = st.sidebar.text_input("username")
role = st.sidebar.selectbox("role", ["student", "instructor", "admin"])

st.title(f"welcome {username}! ({role})")

left, right = st.columns([3,1])
with left:
    st.info("this is the main content area")
with right:
    st.metric("status", "online")
    st.metric("latency", "12ms")
    