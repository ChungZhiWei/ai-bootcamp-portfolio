import streamlit as st

st.title("model comparison tool")
max_tokens = st.slider("max tokens", 50, 500, 150)

col1, col2 = st.columns(2)
with col1:
    st.subheader("model a")
    st.text_area("response a", height=200)
with col2:
    st.subheader("model b")
    st.text_area("response b", height=200)

st.caption(f"comparing responses generated with max_tokens = {max_tokens}")
