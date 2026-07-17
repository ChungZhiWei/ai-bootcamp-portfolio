import streamlit as st

age = st.number_input("enter your age", min_value=0, step=1)

if st.button("check"):
    if age >= 18:
        st.success("you are old enough")
    else:
        st.warning("sorry, you must be 18 or older")