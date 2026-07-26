
"""

A simple username/password login system for app.py, implemented as a
separate Flask Blueprint so it can be developed and reasoned about
independently of the map/editing routes.
 
Wiring it into app.py:
    from auth import auth_bp, login_required
    app.register_blueprint(auth_bp)
 
    @app.route("/nodes")
    @login_required
    def list_nodes():
        ...
"""
 
from functools import wraps
from flask import Blueprint, request, redirect, url_for, session, render_template, flash
from werkzeug.security import generate_password_hash, check_password_hash
 
auth_bp = Blueprint("auth", __name__)
 
# Demo credentials: username "admin", password "admin".
# Change the password (and ideally move this to an env var / real DB)
# before using this anywhere other than local development.
USERS = {
    "admin": generate_password_hash("admin"),
}
 
 
def login_required(view_func):
    """Decorator: redirects to the login page if the user isn't logged in,
    then sends them back to the page they originally wanted afterwards."""
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not session.get("logged_in"):
            flash("Please log in to access this page.", "error")
            return redirect(url_for("auth.login", next=request.path))
        return view_func(*args, **kwargs)
    return wrapped_view
 
 
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        stored_hash = USERS.get(username)
 
        if stored_hash and check_password_hash(stored_hash, password):
            session["logged_in"] = True
            session["username"] = username
            flash(f"Welcome, {username}.", "success")
            next_url = request.args.get("next") or url_for("list_nodes")
            return redirect(next_url)
 
        flash("Invalid username or password.", "error")
        return redirect(url_for("auth.login"))
 
    return render_template("login.html")
 
 
@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))


# label, fill color, marker shape ('s'=square, 'o'=circle, 'D'=diamond,
# '^'=triangle, 'P'=plus) -- used by app.py for rendering, kept here
# alongside the data it describes.
TYPE_STYLE = {
    0: ("Square", "#17D217", "s"),        # square
    1: ("Circle", "#D8DD52", "o"),          # circle
    2: ("Diamond", "#524EC4", "D"),          # diamond
    3: ("Triangle", "#5B5B5B", "^"),  # triangle
    4: ("Plus", "#FF0000", "P"),   # plus
}
DEFAULT_STYLE = ("Unknown", "#777777", "x")
 
NODE_HEADER = (
    "# Node_Info.txt\n"
    "# Format:\n"
    "# NodeID  X   Y   TypeID  Name\n"
    "#\n"
    "# TypeID:\n"
    "# 0 = School\n"
    "# 1 = Shop\n"
    "# 2 = Mall\n"
    "# 3 = HDB / Residential\n"
    "# 4 = Park / Open Area\n\n"
)
 
EDGE_HEADER = (
    "# Graph_Path.txt\n"
    "# Format:\n"
    "# EdgeID  NodeA  NodeB  Distance\n"
    "#\n"
    "# Notes:\n"
    "# - Edges are undirected.\n"
    "# - Distance is the pathfinding cost.\n\n"
)

NODE_FILE = "Node_Info.txt"
EDGE_FILE = "Graph_Path.txt"
 
# ---------------------------------------------------------------------------
# File I/O
# ---------------------------------------------------------------------------
def load_nodes(path):
    nodes_data = {}
    with open(path, "r") as f:
        for line in f:
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            parts = line.split()
            node_id = int(parts[0])
            nodes_data[node_id] = {
                "x": float(parts[1]),
                "y": float(parts[2]),
                "type_id": int(parts[3]),
                "name": parts[4] if len(parts) > 4 else f"Node_{node_id}",
            }
    return nodes_data
 
 
def load_edges(path):
    edges_data = {}
    with open(path, "r") as f:
        for line in f:
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            parts = line.split()
            edge_id = int(parts[0])
            edges_data[edge_id] = {
                "a": int(parts[1]),
                "b": int(parts[2]),
                "distance": float(parts[3]),
            }
    return edges_data
 
 
def save_nodes(path, nodes_data):
    with open(path, "w") as f:
        f.write(NODE_HEADER)
        for node_id in sorted(nodes_data.keys()):
            v = nodes_data[node_id]
            f.write(f"{node_id}\t{v['x']}\t{v['y']}\t{v['type_id']}\t{v['name']}\n")
 
 
def save_edges(path, edges_data):
    with open(path, "w") as f:
        f.write(EDGE_HEADER)
        for edge_id in sorted(edges_data.keys()):
            v = edges_data[edge_id]
            f.write(f"{edge_id}\t{v['a']}\t{v['b']}\t{v['distance']}\n")
 
 
# In-memory state, loaded once when this module is first imported.
NODES_DATA = load_nodes(NODE_FILE)
EDGES_DATA = load_edges(EDGE_FILE)
 
 
def edges_as_tuples(edges_data=None):
    """Adapter: dict form -> [(a, b, distance), ...] for graph/SVG code in app.py."""
    edges_data = EDGES_DATA if edges_data is None else edges_data
    return [(v["a"], v["b"], v["distance"]) for v in edges_data.values()]
 
 
def next_id(existing_ids):
    return (max(existing_ids) + 1) if existing_ids else 0
 
 
# ---------------------------------------------------------------------------
# Node editing
# ---------------------------------------------------------------------------
def add_node(x, y, type_id, name):
    name = (name or "").strip()
    if not name:
        raise ValueError("Name cannot be empty.")
    node_id = next_id(NODES_DATA.keys())
    NODES_DATA[node_id] = {"x": float(x), "y": float(y), "type_id": int(type_id), "name": name}
    save_nodes(NODE_FILE, NODES_DATA)
    return node_id
 
 
def update_node(node_id, x, y, type_id, name):
    if node_id not in NODES_DATA:
        raise KeyError(f"Node {node_id} does not exist.")
    name = (name or "").strip()
    if not name:
        raise ValueError("Name cannot be empty.")
    NODES_DATA[node_id] = {"x": float(x), "y": float(y), "type_id": int(type_id), "name": name}
    save_nodes(NODE_FILE, NODES_DATA)
 
 
def delete_node(node_id):
    """Deletes a node and cascade-deletes any edges that referenced it.
    Returns (node_name, num_edges_removed)."""
    if node_id not in NODES_DATA:
        raise KeyError(f"Node {node_id} does not exist.")
 
    name = NODES_DATA[node_id]["name"]
    del NODES_DATA[node_id]
 
    orphaned = [eid for eid, e in EDGES_DATA.items() if e["a"] == node_id or e["b"] == node_id]
    for eid in orphaned:
        del EDGES_DATA[eid]
 
    save_nodes(NODE_FILE, NODES_DATA)
    save_edges(EDGE_FILE, EDGES_DATA)
    return name, len(orphaned)
 
 
# ---------------------------------------------------------------------------
# Edge editing
# ---------------------------------------------------------------------------
def _validate_edge(a, b, distance):
    a, b, distance = int(a), int(b), float(distance)
    if a not in NODES_DATA or b not in NODES_DATA:
        raise ValueError("Both nodes must exist.")
    if a == b:
        raise ValueError("A path cannot connect a node to itself.")
    if distance <= 0:
        raise ValueError("Distance must be greater than 0.")
    return a, b, distance
 
 
def add_edge(a, b, distance):
    a, b, distance = _validate_edge(a, b, distance)
    edge_id = next_id(EDGES_DATA.keys())
    EDGES_DATA[edge_id] = {"a": a, "b": b, "distance": distance}
    save_edges(EDGE_FILE, EDGES_DATA)
    return edge_id
 
 
def update_edge(edge_id, a, b, distance):
    if edge_id not in EDGES_DATA:
        raise KeyError(f"Path {edge_id} does not exist.")
    a, b, distance = _validate_edge(a, b, distance)
    EDGES_DATA[edge_id] = {"a": a, "b": b, "distance": distance}
    save_edges(EDGE_FILE, EDGES_DATA)
 
 
def delete_edge(edge_id):
    if edge_id not in EDGES_DATA:
        raise KeyError(f"Path {edge_id} does not exist.")
    del EDGES_DATA[edge_id]
    save_edges(EDGE_FILE, EDGES_DATA)
 