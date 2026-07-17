import streamlit as st

st.title("greeting app")
name = st.text_input("enter your name")

if st.button("greet me"):
    st.markdown(f"## hello, {name}!")
