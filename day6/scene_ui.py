import streamlit as st

#streamlit run scene_ui.py

st.title("Scene Object Manager")

if "scene_objects" not in st.session_state:
    st.session_state.scene_objects = []
if "next_id" not in st.session_state:
    st.session_state.next_id = 1

st.header("Add a new object")
name = st.text_input("Name")
x = st.number_input("X", value=0.0)
y = st.number_input("Y", value=0.0)
z = st.number_input("Z", value=0.0)

if st.button("Add Object"):
    if not name:
        st.warning("Name is required.")
    else:
        st.session_state.scene_objects.append({
            "id": st.session_state.next_id,
            "name": name,
            "position": [x, y, z],
        })
        st.session_state.next_id += 1

st.header("Current objects")
if not st.session_state.scene_objects:
    st.info("No objects yet.")
for obj in st.session_state.scene_objects:
    col1, col2 = st.columns([4, 1])
    with col1:
        st.write(f"**#{obj['id']} {obj['name']}** — position {obj['position']}")
    with col2:
        if st.button("Delete", key=f"delete_{obj['id']}"):
            st.session_state.scene_objects = [
                o for o in st.session_state.scene_objects if o["id"] != obj["id"]
            ]
            st.rerun()


