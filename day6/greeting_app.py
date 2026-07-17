import streamlit as st

st.title("Greeting App")
name = st.text_input("Enter your name")

if st.button("Greet Me"):
    st.write(f"Hello {name}")

age = st.number_input("Enter your age", min_value=0, step=1)
if st.button("Greet Me Age"):
    st.write(f"Hello {name}, you are {int(age)} years old")

if name:
    st.write(f"Hello {name}")


st.sidebar.title("Profile")
name = st.sidebar.text_input("Name")
role = st.sidebar.text_input("Role")

st.write(f"Welcome {name}")
st.write(f"Role: {role}")

role = st.sidebar.selectbox("Role", ["Student", "Admin"])

if role == "Admin":
    st.success("Full Access Granted")
else:
    st.warning("Limited Access")

left, right = st.columns(2)
with left:
    st.write("Some text content here.")
with right:
    st.metric("Users", 120)
    st.metric("Status", "Active")

left, right = st.columns([3, 1])
with left:
    st.info("This is the wide column.")
with right:
    st.write("Narrow column")

file = st.file_uploader("Upload a file", type=["txt"])
if file:
    st.write(f"File name: {file.name}")

if file:
    content = file.read().decode("utf-8")
    st.write(content)

st.title("Resume Analyzer")
resume = st.file_uploader("Upload your resume", type=["pdf", "txt"])
if resume:
    st.success("Resume uploaded successfully!")

if "count" not in st.session_state:
    st.session_state.count = 0

if st.button("Add +1"):
    st.session_state.count += 1

st.write(st.session_state.count)

if st.button("Reset"):
    st.session_state.count = 0

if st.button("Subtract -1"):
    if st.session_state.count > 0:
        st.session_state.count -= 1


