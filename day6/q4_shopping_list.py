import streamlit as st

if "shopping_list" not in st.session_state:
    st.session_state.shopping_list = []

item = st.text_input("add item")
col1, col2 = st.columns(2)
with col1:
    if st.button("add") and item:
        st.session_state.shopping_list.append(item)
with col2:
    if st.button("clear all"):
        st.session_state.shopping_list = []

st.write("your list")
for i, thing in enumerate(st.session_state.shopping_list, start = 1):
    st.write(f"{i}, {thing}")

