import streamlit as st

st.title("the persistant counter")
count = 0

if "count" not in st.session_state:
    st.session_state["count"] = 0

col1, col2 = st.columns(2)
with col1:
    if st.button("add 1"):
        count += 1
        st.session_state["count"] += 1
with col2:
    if st.button("reset"):
        count = 0
        st.session_state["count"] = 0

st.write(f"with session state: {st.session_state["count"]}")
st.write(f"without session state: {count}")


