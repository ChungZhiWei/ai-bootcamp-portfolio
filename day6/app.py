from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello from Flask!"

@app.route("/greet", methods=["GET"])
def greet():
    return "Send me a POST with your name!"

@app.route("/greet", methods=["POST"])
def greet_post():
    return "Thanks, got your POST."

@app.route("/square/<int:n>")
def square(n):
    return str(n * n)

@app.route("/greet/<name>")
def greet_name(name):
    return f"Hello, {name}!"

@app.route("/search")
def search():
    # GET /search?q=vulkan&limit=5
    query = request.args.get("q", "")
    limit = request.args.get("limit", 10, type=int)
    return f"Searching for '{query}', limit={limit}"

@app.route("/vector/dot", methods=["POST"])
def dot_product():
    data = request.get_json()
    a, b = data["a"], data["b"]
    result = sum(x * y for x, y in zip(a, b))
    return jsonify({"result": result})

scene_objects = []   # list of dicts — gone on restart
next_id = 1

@app.route("/objects", methods=["GET"])
def list_objects():
    return jsonify(scene_objects)

@app.route("/objects", methods=["POST"])
def add_object():
    global next_id
    data = request.get_json()
    obj = {"id": next_id, "name": data["name"], "position": data.get("position", [0, 0, 0])}
    scene_objects.append(obj)
    next_id += 1
    return jsonify(obj), 201          # 201 Created

@app.route("/objects/<int:obj_id>", methods=["DELETE"])
def delete_object(obj_id):
    global scene_objects
    scene_objects = [o for o in scene_objects if o["id"] != obj_id]
    return jsonify({"status": "deleted"})

@app.route("/objects/<int:obj_id>", methods=["GET"])
def get_object(obj_id):
    for obj in scene_objects:
        if obj["id"] == obj_id:
            return jsonify(obj)
    return jsonify({"error": "not found"}), 404

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "That route doesn't exist"}), 404



if __name__ == "__main__":
    app.run(debug=True)



'''
import streamlit as st

#streamlit run app.py

st.title("My First AI App")
name = st.text_input("Enter your name")

if st.button("Click Me"):
    st.write(f"Hello {name} 👋")

st.sidebar.title("Settings")
st.sidebar.markdown("Please enter your username")
username = st.sidebar.text_input("Enter Username", value="Admin")
role = st.sidebar.selectbox("Role", ["Student", "Instructor", "Admin"])

st.title(f"Welcome, {username}! ({role})")

left_col, right_col = st.columns([3, 1])   # 3:1 width ratio

with left_col:
    st.header("Main Content")
    st.write("This is the primary area for your data or chat interface.")
    st.info("Notice how this column stays wide while the other is narrow.")

with right_col:
    st.header("Stats")
    st.metric(label="System Status", value="Online")
    st.metric(label="Latency", value="12ms")

uploaded_file = st.file_uploader("Upload your resume", type=["pdf", "txt"])

if uploaded_file:                       # None until the user uploads
    st.success("File uploaded!")
    st.write(f"The file name is: {uploaded_file.name}")

if uploaded_file:
    text = uploaded_file.read().decode("utf-8")   # plain text files
    # or: pandas.read_csv(uploaded_file)
    # or: PIL.Image.open(uploaded_file)

st.title("The Persistent Counter")
count = 0                                        # normal variable — resets every rerun

if "count" not in st.session_state:              # init guard — runs once per session
    st.session_state["count"] = 0

def increment_counter():
    st.session_state["count"] += 1

def reset_counter():
    st.session_state["count"] = 0

col1, col2 = st.columns(2)
with col1:
    if st.button("Add +1"):
        count += 1
        increment_counter()
with col2:
    if st.button("Reset"):
        count = 0
        reset_counter()

st.write(f"Current Count (with Session State): **{st.session_state['count']}**")
st.write(f"Current Count (without Session State): **{count}**")   # never exceeds 1

if user_input := st.chat_input("Say something"):
    with st.chat_message("user"):
        st.markdown(user_input)
    with st.chat_message("assistant"):
        st.markdown(f"You said: {user_input}")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_input := st.chat_input("Type your message..."):
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    reply = f"Echo: {user_input}"          # Later: replace with a real LLM call
    with st.chat_message("assistant"):
        st.markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
'''
