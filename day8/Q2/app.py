from flask import Flask, render_template, request, redirect, url_for, flash
from markupsafe import escape

from Pathfinder import find_shortest_distance
from Map import build_svg
import EditorAuthentication

app = Flask(__name__)
app.secret_key = "dev-only-change-me"  # required for sessions/flash; replace for real deployments
app.register_blueprint(EditorAuthentication.auth_bp)

NODE_FILE = "Node_Info.txt"
EDGE_FILE = "Graph_Path.txt"

nodes_data = {}
edges_data = {}

def loadFile(filePath):
    output = []
    with open(filePath, "r", encoding="utf-8") as data:
        for line in data:
            if not line.startswith('\n') and not line.startswith('#'):
                output.append(line.strip())
    return output

def parse_edges(data):
    """Return list of (a, b, distance) tuples."""
    edges = []
    for line in data:
        parts = line.split()
        edges.append((int(parts[1]), int(parts[2]), float(parts[3])))
    return edges

def parse_nodes(data):
    """Returns dict: node_id -> {x, y, type_id, name}"""
    nodes = {}
    for line in data:
        parts = line.split()
        node_id, x, y, type_id = int(parts[0]), float(parts[1]), float(parts[2]), int(parts[3])
        name = parts[4]
        nodes[node_id] = {"x": x, "y": y, "type_id": type_id, "name": name}
    return nodes

@app.route("/")
def index():
    global nodes_data
    nodes_data = parse_nodes(loadFile(NODE_FILE))
    global edges_data
    edges_data = parse_edges(loadFile(EDGE_FILE))

    start = request.args.get("start", type=int)
    destination = request.args.get("destination", type=int)

    highlight_path = None
    formatted_message = None
    error = None

    if start is not None and destination is not None:
        output = find_shortest_distance(edges_data, start, destination)
        if isinstance(output, str):
            error = output
        else:
            highlight_path, distance, formatted_message = output
 
    svg_markup = build_svg(nodes_data, edges_data, highlight_path=highlight_path)
    path_names = [nodes_data[n]["name"] for n in highlight_path] if highlight_path else []
    formatted_message = str(escape(formatted_message)).replace('\n', '<br>')
    
    return render_template(
        "index.html",
        svg_markup=svg_markup,
        nodes=sorted(nodes_data.items()),
        start=start,
        destination=destination,
        highlight_path=highlight_path,
        message=formatted_message,
        error=error,
    )


# ---------------------------------------------------------------------------
# Node CRUD (requires login)
# ---------------------------------------------------------------------------
@app.route("/nodes", methods=["GET"])
@EditorAuthentication.login_required
def list_nodes():
    return render_template(
        "nodes.html",
        nodes=sorted(EditorAuthentication.NODES_DATA.items()),
        type_style=EditorAuthentication.TYPE_STYLE,
    )
 
 
@app.route("/nodes/add", methods=["GET", "POST"])
@EditorAuthentication.login_required
def add_node():
    if request.method == "POST":
        try:
            node_id = EditorAuthentication.add_node(
                x=request.form["x"],
                y=request.form["y"],
                type_id=request.form["type_id"],
                name=request.form["name"],
            )
        except (KeyError, ValueError) as e:
            flash(f"Could not add node: {e}", "error")
            return redirect(url_for("add_node"))

        global nodes_data
        nodes_data = parse_nodes(loadFile(NODE_FILE))

        flash(f"Added node {node_id}.", "success")
        return redirect(url_for("list_nodes"))


    return render_template("node_form.html", node=None, node_id=None, type_style=EditorAuthentication.TYPE_STYLE)
 
 
@app.route("/nodes/edit/<int:node_id>", methods=["GET", "POST"])
@EditorAuthentication.login_required
def edit_node(node_id):
    if node_id not in EditorAuthentication.NODES_DATA:
        flash(f"Node {node_id} does not exist.", "error")
        return redirect(url_for("list_nodes"))
 
    if request.method == "POST":
        try:
            EditorAuthentication.update_node(
                node_id,
                x=request.form["x"],
                y=request.form["y"],
                type_id=request.form["type_id"],
                name=request.form["name"],
            )
        except (KeyError, ValueError) as e:
            flash(f"Could not update node: {e}", "error")
            return redirect(url_for("edit_node", node_id=node_id))

        global nodes_data
        nodes_data = parse_nodes(loadFile(NODE_FILE))

        flash(f"Updated node {node_id}.", "success")
        return redirect(url_for("list_nodes"))
 
    return render_template("node_form.html", node=EditorAuthentication.NODES_DATA[node_id], node_id=node_id, type_style=EditorAuthentication.TYPE_STYLE)
 
 
@app.route("/nodes/delete/<int:node_id>", methods=["POST"])
@EditorAuthentication.login_required
def delete_node(node_id):
    try:
        name, orphaned_count = EditorAuthentication.delete_node(node_id)
    except KeyError as e:
        flash(str(e), "error")
        return redirect(url_for("list_nodes"))

    global nodes_data
    nodes_data = parse_nodes(loadFile(NODE_FILE))
    
    msg = f"Deleted node {node_id} ({name})."
    if orphaned_count:
        msg += f" Also removed {orphaned_count} connected edge(s)."
    flash(msg, "success")
    return redirect(url_for("list_nodes"))
 
 
# ---------------------------------------------------------------------------
# Edge CRUD (requires login)
# ---------------------------------------------------------------------------
@app.route("/edges", methods=["GET"])
@EditorAuthentication.login_required
def list_edges():
    return render_template(
        "edges.html",
        edges=sorted(EditorAuthentication.EDGES_DATA.items()),
        nodes_data=EditorAuthentication.NODES_DATA,
    )
 
 
@app.route("/edges/add", methods=["GET", "POST"])
@EditorAuthentication.login_required
def add_edge():
    if request.method == "POST":
        try:
            edge_id = EditorAuthentication.add_edge(
                a=request.form["node_a"],
                b=request.form["node_b"],
                distance=request.form["distance"],
            )
        except (KeyError, ValueError) as e:
            flash(f"Could not add path: {e}", "error")
            return redirect(url_for("add_edge"))

        global edges_data
        edges_data = parse_edges(loadFile(EDGE_FILE))

        flash(f"Added path {edge_id}.", "success")
        return redirect(url_for("list_edges"))
 
    return render_template("edge_form.html", edge=None, edge_id=None, nodes_data=EditorAuthentication.NODES_DATA)
 
 
@app.route("/edges/edit/<int:edge_id>", methods=["GET", "POST"])
@EditorAuthentication.login_required
def edit_edge(edge_id):
    if edge_id not in EditorAuthentication.EDGES_DATA:
        flash(f"Path {edge_id} does not exist.", "error")
        return redirect(url_for("list_edges"))
 
    if request.method == "POST":
        try:
            EditorAuthentication.update_edge(
                edge_id,
                a=request.form["node_a"],
                b=request.form["node_b"],
                distance=request.form["distance"],
            )
        except (KeyError, ValueError) as e:
            flash(f"Could not update path: {e}", "error")
            return redirect(url_for("edit_edge", edge_id=edge_id))

        global edges_data
        edges_data = parse_edges(loadFile(EDGE_FILE))

        flash(f"Updated path {edge_id}.", "success")
        return redirect(url_for("list_edges"))
 
    return render_template("edge_form.html", edge=EditorAuthentication.EDGES_DATA[edge_id], edge_id=edge_id, nodes_data=EditorAuthentication.NODES_DATA)
 
 
@app.route("/edges/delete/<int:edge_id>", methods=["POST"])
@EditorAuthentication.login_required
def delete_edge(edge_id):
    try:
        EditorAuthentication.delete_edge(edge_id)
    except KeyError as e:
        flash(str(e), "error")
        return redirect(url_for("list_edges"))

    global edges_data
    edges_data = parse_edges(loadFile(EDGE_FILE))
    
    flash(f"Deleted path {edge_id}.", "success")
    return redirect(url_for("list_edges"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)