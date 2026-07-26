# TypeID -> (label, color, marker shape)
TYPE_STYLE = {
    0: ("Square", "#17D217", "s"),        # square
    1: ("Circle", "#D8DD52", "o"),          # circle
    2: ("Diamond", "#524EC4", "D"),          # diamond
    3: ("Triangle", "#5B5B5B", "^"),  # triangle
    4: ("Plus", "#FF0000", "P"),   # plus
}
DEFAULT_STYLE = ("Unknown", "#777777", "x")
 
 
# ---------------------------------------------------------------------------
# SVG rendering helpers (replaces the matplotlib ax.scatter/ax.plot calls)
# ---------------------------------------------------------------------------
def marker_svg(marker, cx, cy, color, size, stroke, stroke_width):
    if marker == "s":  # square
        return (f'<rect x="{cx - size}" y="{cy - size}" width="{size * 2}" '
                f'height="{size * 2}" fill="{color}" stroke="{stroke}" '
                f'stroke-width="{stroke_width}" />')
    if marker == "o":  # circle
        return (f'<circle cx="{cx}" cy="{cy}" r="{size}" fill="{color}" '
                f'stroke="{stroke}" stroke-width="{stroke_width}" />')
    if marker == "D":  # diamond
        pts = f"{cx},{cy-size} {cx+size},{cy} {cx},{cy+size} {cx-size},{cy}"
        return (f'<polygon points="{pts}" fill="{color}" stroke="{stroke}" '
                f'stroke-width="{stroke_width}" />')
    if marker == "^":  # triangle
        pts = f"{cx},{cy-size} {cx+size},{cy+size} {cx-size},{cy+size}"
        return (f'<polygon points="{pts}" fill="{color}" stroke="{stroke}" '
                f'stroke-width="{stroke_width}" />')
    if marker == "P":  # plus
        w = size * 0.5
        pts = (f"{cx-w},{cy-size} {cx+w},{cy-size} {cx+w},{cy-w} "
               f"{cx+size},{cy-w} {cx+size},{cy+w} {cx+w},{cy+w} "
               f"{cx+w},{cy+size} {cx-w},{cy+size} {cx-w},{cy+w} "
               f"{cx-size},{cy+w} {cx-size},{cy-w} {cx-w},{cy-w}")
        return (f'<polygon points="{pts}" fill="{color}" stroke="{stroke}" '
                f'stroke-width="{stroke_width}" />')
    # fallback: X mark
    return (f'<line x1="{cx-size}" y1="{cy-size}" x2="{cx+size}" y2="{cy+size}" '
            f'stroke="{color}" stroke-width="{stroke_width + 2}" />'
            f'<line x1="{cx-size}" y1="{cy+size}" x2="{cx+size}" y2="{cy-size}" '
            f'stroke="{color}" stroke-width="{stroke_width + 2}" />')
 
 
def build_svg(nodes_data, edges_data, highlight_path=None,
              width=900, height=650, padding=60):
    xs = [v["x"] for v in nodes_data.values()]
    ys = [v["y"] for v in nodes_data.values()]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span_x = (max_x - min_x) or 1
    span_y = (max_y - min_y) or 1
    scale = min((width - 2 * padding) / span_x, (height - 2 * padding) / span_y)
 
    def transform(x, y):
        px = padding + (x - min_x) * scale
        py = height - (padding + (y - min_y) * scale)  # flip so +y is "up"
        return px, py
 
    coords = {node_id: transform(v["x"], v["y"]) for node_id, v in nodes_data.items()}
    highlight_set = set(highlight_path) if highlight_path else set()
    highlight_edges = set()
    if highlight_path and len(highlight_path) > 1:
        for a, b in zip(highlight_path, highlight_path[1:]):
            highlight_edges.add(frozenset((a, b)))
 
    svg_parts = [f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
                 f'style="background:#ffffff;font-family:sans-serif;">']
 
    # --- background edges ---
    for a, b, _dist in edges_data:
        if a not in coords or b not in coords:
            continue
        is_highlighted = frozenset((a, b)) in highlight_edges
        if is_highlighted:
            continue  # drawn on top separately
        xa, ya = coords[a]
        xb, yb = coords[b]
        svg_parts.append(f'<line x1="{xa}" y1="{ya}" x2="{xb}" y2="{yb}" '
                          f'stroke="#B0B0B0" stroke-width="1.5" stroke-linecap="round" />')
 
    # --- highlighted path edges (drawn on top, bold red) ---
    for a, b in zip(highlight_path or [], (highlight_path or [])[1:]):
        if a not in coords or b not in coords:
            continue
        xa, ya = coords[a]
        xb, yb = coords[b]
        svg_parts.append(f'<line x1="{xa}" y1="{ya}" x2="{xb}" y2="{yb}" '
                          f'stroke="#E63946" stroke-width="4" stroke-linecap="round" />')
 
    # --- nodes + labels ---
    plotted_types = set()
    legend_entries = []
    for node_id, v in nodes_data.items():
        cx, cy = coords[node_id]
        type_id = v["type_id"]
        name = v["name"]
        label, color, marker = TYPE_STYLE.get(type_id, DEFAULT_STYLE)
 
        is_on_path = node_id in highlight_set
        stroke = "#E63946" if is_on_path else "black"
        stroke_width = 3 if is_on_path else 1
 
        svg_parts.append(marker_svg(marker, cx, cy, color, 10, stroke, stroke_width))
        svg_parts.append(f'<text x="{cx}" y="{cy - 16}" text-anchor="middle" '
                          f'font-size="11">{name}</text>')
 
        if type_id not in plotted_types:
            plotted_types.add(type_id)
            legend_entries.append((label, color, marker))
 
    # --- legend ---
    lx, ly = width - 190, 20
    svg_parts.append(f'<rect x="{lx - 10}" y="{ly - 10}" width="180" '
                      f'height="{20 * len(legend_entries) + 20}" fill="white" '
                      f'stroke="#cccccc" />')
    for i, (label, color, marker) in enumerate(legend_entries):
        ey = ly + i * 20 + 10
        svg_parts.append(marker_svg(marker, lx + 8, ey, color, 7, "black", 1))
        svg_parts.append(f'<text x="{lx + 22}" y="{ey + 4}" font-size="11">{label}</text>')
 
    svg_parts.append("</svg>")
    return "".join(svg_parts)

