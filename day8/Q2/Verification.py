#!/usr/bin/env python3
"""
verify_app.py
=============
Command-line verification / smoke-test suite for the Node-Map Flask app
(app.py + EditorAuthentication.py + Pathfinder.py + Map.py).

What it does
------------
1. Starts the real Flask app as a subprocess and waits for it to accept
   connections (with the debug auto-reloader turned off, since that's a
   dev-only feature that just adds a second process to manage).
2. Drives it over real HTTP with `requests`, exactly like a browser would.
3. Cross-checks the app's pathfinding answers against an INDEPENDENT
   reference implementation (Bellman-Ford, re-parsed straight from
   Graph_Path.txt) rather than re-using Pathfinder.py, so a bug in the
   app's own Dijkstra code would actually be caught.
4. Prints a PASS/FAIL table with input / expected / actual for every
   test case, and writes a human-readable report file.
5. Exits 0 on full success, 1 if any test failed, 2 on infra failure
   (e.g. the app never came up) - handy for scripting / `&&` chains.

Usage
-----
    python3 verify_app.py
    python3 verify_app.py --app-dir /path/to/app --port 5050
    python3 verify_app.py --help

Run it from the same directory as app.py, or point it there with --app-dir.
"""

import argparse
import html
import os
import re
import signal
import sys
import time
import socket
import subprocess
from dataclasses import dataclass
from typing import List, Optional, Tuple

import requests

# --------------------------------------------------------------------------
# Configuration (overridable via CLI flags - see parse_args())
# --------------------------------------------------------------------------
APP_HOST = "127.0.0.1"
STARTUP_TIMEOUT = 20  # seconds to wait for the server socket to open
LOGIN_USER = "admin"
LOGIN_PASS = "admin"

# Populated in main() from parsed CLI args; module-level so the test
# functions below can reference them without threading extra params
# through every call.
APP_DIR = os.path.dirname(os.path.abspath(__file__))
APP_PORT = 5000
BASE_URL = f"http://{APP_HOST}:{APP_PORT}"
EDGE_FILE = os.path.join(APP_DIR, "Graph_Path.txt")
REPORT_TXT = os.path.join(APP_DIR, "verification_report.txt")


# --------------------------------------------------------------------------
# Result bookkeeping
# --------------------------------------------------------------------------
@dataclass
class TestResult:
    tc_id: str
    name: str
    test_input: str
    expected: str
    actual: str = ""
    passed: bool = False
    error: str = ""


RESULTS: List[TestResult] = []


def record(tc_id, name, test_input, expected, actual, passed, error=""):
    r = TestResult(tc_id, name, test_input, expected, actual, passed, error)
    RESULTS.append(r)
    status = "PASS" if passed else "FAIL"
    print(f"\n[{status}] {tc_id} - {name}")
    print(f"    Input:    {test_input}")
    print(f"    Expected: {expected}")
    print(f"    Actual:   {actual}")
    if error:
        print(f"    Error:    {error}")
    return r


def run_safely(tc_id, name, fn, *args):
    """Run a test function; if it throws before recording a result itself,
    log that as a FAIL instead of crashing the whole suite."""
    before = len(RESULTS)
    try:
        fn(*args)
    except Exception as e:  # noqa: BLE001 - deliberately broad for a test harness
        if len(RESULTS) == before:
            record(tc_id, name, "N/A", "No exception raised",
                   f"Exception occurred: {e!r}", False, error=str(e))


# --------------------------------------------------------------------------
# Independent reference oracle (Bellman-Ford, deliberately NOT the app's
# own Dijkstra code, and NOT importing Pathfinder.py)
# --------------------------------------------------------------------------
def load_reference_edges(path) -> List[Tuple[int, int, float]]:
    edges = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            parts = line.split()
            edges.append((int(parts[1]), int(parts[2]), float(parts[3])))
    return edges


def reference_shortest_path(edges, start, dest):
    """Returns ([path...], distance) or None (unreachable) or the strings
    'INVALID_START' / 'INVALID_END' if the node never appears in any edge."""
    nodes = set()
    for a, b, _ in edges:
        nodes.add(a)
        nodes.add(b)

    if start not in nodes:
        return "INVALID_START"
    if dest not in nodes:
        return "INVALID_END"
    if start == dest:
        return ([start], 0.0)

    dist = {n: float("inf") for n in nodes}
    prev = {n: None for n in nodes}
    dist[start] = 0.0

    for _ in range(len(nodes) - 1):
        changed = False
        for a, b, w in edges:
            if dist[a] + w < dist[b]:
                dist[b] = dist[a] + w
                prev[b] = a
                changed = True
            if dist[b] + w < dist[a]:
                dist[a] = dist[b] + w
                prev[a] = b
                changed = True
        if not changed:
            break

    if dist[dest] == float("inf"):
        return None

    path, node = [], dest
    while node is not None:
        path.append(node)
        node = prev[node]
    path.reverse()
    return (path, dist[dest])


# --------------------------------------------------------------------------
# Server lifecycle
# --------------------------------------------------------------------------
def wait_for_port(host, port, timeout) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.3)
    return False


def start_server() -> Optional[subprocess.Popen]:
    # NOTE: we deliberately do NOT run `python3 app.py` directly. app.py's
    # __main__ block calls app.run(debug=True), and Flask's debug mode
    # spawns a second "reloader" watcher process. That reloader is a dev
    # convenience with no purpose in CI, and on some non-interactive
    # runners (containers, Jenkins agents without a real tty) it can
    # prevent the process tree from ever being cleanly reaped, hanging
    # the build. Instead we import app.py as a module (which still runs
    # all of its route/blueprint registration exactly as normal) and
    # start the server ourselves with the reloader turned off.
    launcher = (
        "import app as _app; "
        "_app.app.run(host='127.0.0.1', port=%d, debug=False, use_reloader=False)"
        % APP_PORT
    )
    proc = subprocess.Popen(
        [sys.executable, "-c", launcher],
        cwd=APP_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
    )

    if not wait_for_port(APP_HOST, APP_PORT, STARTUP_TIMEOUT):
        proc.terminate()
        try:
            out, _ = proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            out = "(timed out reading process output)"
        print("Server failed to start within the timeout. Output:\n", out)
        return None
    time.sleep(1.0)  # let Flask finish binding all routes
    return proc


def stop_server(proc):
    if proc is None:
        return
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    except (ProcessLookupError, PermissionError, OSError):
        proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError, OSError):
            proc.kill()



# --------------------------------------------------------------------------
# HTML scraping helpers (avoids adding a JSON API just for tests)
# --------------------------------------------------------------------------
def parse_path_message(page_html):
    m = re.search(
        r"Shortest path:<br>([^<]+)<br>Total distance:<br>([^<]+)<br>", page_html
    )
    if not m:
        return None, None
    path_str, dist_str = m.groups()
    # The app HTML-escapes the message (">" becomes "&gt;"), so "->"
    # renders as "-&gt;" in the page source. Unescape before parsing.
    path_str = html.unescape(path_str)
    path = [int(x.strip()) for x in path_str.split("->")]
    dist = float(dist_str.strip())
    return path, dist


def parse_error_message(page_html):
    m = re.search(r'<div class="result error">\s*([^<]+?)\s*</div>', page_html)
    return m.group(1).strip() if m else None


def login(session):
    session.get(f"{BASE_URL}/login")
    return session.post(
        f"{BASE_URL}/login", data={"username": LOGIN_USER, "password": LOGIN_PASS}
    )


# --------------------------------------------------------------------------
# Test cases
# --------------------------------------------------------------------------
def tc1_normal_shortest_path(session, ref_edges):
    start, dest = 0, 3
    resp = session.get(f"{BASE_URL}/", params={"start": start, "destination": dest})
    expected = reference_shortest_path(ref_edges, start, dest)
    path, dist = parse_path_message(resp.text)
    passed = (
        resp.status_code == 200
        and isinstance(expected, tuple)
        and path == expected[0]
        and dist == expected[1]
    )
    record(
        "TC1", "Normal shortest path",
        f"GET /?start={start}&destination={dest}",
        f"path={expected[0] if isinstance(expected, tuple) else expected}, "
        f"distance={expected[1] if isinstance(expected, tuple) else '-'}",
        f"status={resp.status_code}, path={path}, distance={dist}",
        passed,
    )


def tc2_start_equals_end(session, ref_edges):
    node = 5
    resp = session.get(f"{BASE_URL}/", params={"start": node, "destination": node})
    path, dist = parse_path_message(resp.text)
    passed = resp.status_code == 200 and path == [node] and dist == 0.0
    record(
        "TC2", "Start node equals end node",
        f"GET /?start={node}&destination={node}",
        f"path=[{node}], distance=0.0 (trivial zero-length path)",
        f"status={resp.status_code}, path={path}, distance={dist}",
        passed,
    )


def tc3_invalid_start(session):
    bad, dest = 9999, 3
    resp = session.get(f"{BASE_URL}/", params={"start": bad, "destination": dest})
    err = parse_error_message(resp.text)
    expected = f"Start node: {bad} is invalid."
    passed = resp.status_code == 200 and err == expected
    record(
        "TC3", "Invalid start node",
        f"GET /?start={bad}&destination={dest}",
        expected,
        f"status={resp.status_code}, error={err!r}",
        passed,
    )


def tc4_invalid_end(session):
    start, bad = 0, 9999
    resp = session.get(f"{BASE_URL}/", params={"start": start, "destination": bad})
    err = parse_error_message(resp.text)
    expected = f"End node: {bad} is invalid."
    passed = resp.status_code == 200 and err == expected
    record(
        "TC4", "Invalid destination node",
        f"GET /?start={start}&destination={bad}",
        expected,
        f"status={resp.status_code}, error={err!r}",
        passed,
    )


def tc5_unreachable_destination(session):
    """Creates two brand-new nodes wired only to each other (a second,
    disconnected component), then confirms the pathfinder reports
    'No Path Exists' rather than 'invalid node'. Cleans up afterwards."""
    ts = str(int(time.time() * 1000))
    node_a = node_b = None
    try:
        for suffix in ("A", "B"):
            session.post(
                f"{BASE_URL}/nodes/add",
                data={"x": "999", "y": "999", "type_id": "4", "name": f"Isolated_{ts}_{suffix}"},
            )

        listing = session.get(f"{BASE_URL}/nodes").text
        ids = {}
        for m in re.finditer(
            rf"<td>(\d+)</td>\s*<td>(Isolated_{ts}_[AB])</td>", listing
        ):
            ids[m.group(2)] = int(m.group(1))
        node_a = ids.get(f"Isolated_{ts}_A")
        node_b = ids.get(f"Isolated_{ts}_B")
        if node_a is None or node_b is None:
            raise RuntimeError("could not find newly-created isolated nodes in /nodes listing")

        session.post(
            f"{BASE_URL}/edges/add",
            data={"node_a": str(node_a), "node_b": str(node_b), "distance": "10"},
        )

        resp = session.get(f"{BASE_URL}/", params={"start": 0, "destination": node_a})
        err = parse_error_message(resp.text)
        expected = "No Path Exists"
        passed = resp.status_code == 200 and err == expected
        record(
            "TC5", "Disconnected graph / unreachable destination",
            f"GET /?start=0&destination={node_a}  "
            f"(node {node_a} exists but is only connected to isolated node {node_b}, "
            f"which has no link to the main graph)",
            expected,
            f"status={resp.status_code}, error={err!r}",
            passed,
        )
    finally:
        # Deleting a node cascades and removes its edges too.
        if node_a is not None:
            session.post(f"{BASE_URL}/nodes/delete/{node_a}")
        if node_b is not None:
            session.post(f"{BASE_URL}/nodes/delete/{node_b}")


def tc6_multiple_paths(session, ref_edges):
    # 0 -> 8 has several candidate routes of differing cost; this exercises
    # that the app actually picks the cheapest one, not just any one.
    start, dest = 0, 8
    resp = session.get(f"{BASE_URL}/", params={"start": start, "destination": dest})
    expected = reference_shortest_path(ref_edges, start, dest)
    path, dist = parse_path_message(resp.text)
    passed = (
        resp.status_code == 200
        and isinstance(expected, tuple)
        and path == expected[0]
        and dist == expected[1]
    )
    record(
        "TC6", "Map with multiple possible paths (true shortest must win)",
        f"GET /?start={start}&destination={dest}",
        f"path={expected[0] if isinstance(expected, tuple) else expected}, "
        f"distance={expected[1] if isinstance(expected, tuple) else '-'}",
        f"status={resp.status_code}, path={path}, distance={dist}",
        passed,
    )


def tc7_unauthorized_editor_access():
    anon = requests.Session()  # never logged in

    resp = anon.get(f"{BASE_URL}/nodes", allow_redirects=False)
    passed = resp.status_code in (301, 302) and "/login" in resp.headers.get("Location", "")
    record(
        "TC7a", "Map-editing route (GET /nodes) rejected for unauthenticated user",
        "GET /nodes with no logged-in session",
        "302 redirect to /login (access denied)",
        f"status={resp.status_code}, Location={resp.headers.get('Location')}",
        passed,
    )

    resp2 = anon.post(
        f"{BASE_URL}/nodes/add",
        data={"x": "1", "y": "1", "type_id": "0", "name": "should_not_be_created"},
        allow_redirects=False,
    )
    passed2 = resp2.status_code in (301, 302) and "/login" in resp2.headers.get("Location", "")
    record(
        "TC7b", "Map-editing route (POST /nodes/add) rejected for unauthenticated user",
        "POST /nodes/add with no logged-in session",
        "302 redirect to /login, no node created",
        f"status={resp2.status_code}, Location={resp2.headers.get('Location')}",
        passed2,
    )


def tc8_public_pathfinding_no_auth():
    anon = requests.Session()  # never logged in
    resp = anon.get(f"{BASE_URL}/", params={"start": 0, "destination": 3})
    passed = resp.status_code == 200 and "Shortest path" in resp.text
    record(
        "TC8", "Public pathfinding works without authentication",
        "GET /?start=0&destination=3 with no session cookie",
        "200 OK, page renders the computed path without requiring login",
        f"status={resp.status_code}, contains_result={'Shortest path' in resp.text}",
        passed,
    )


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------
def write_report():
    with open(REPORT_TXT, "w", encoding="utf-8") as f:
        f.write("Automated Verification Report\n")
        f.write("=" * 72 + "\n\n")
        for r in RESULTS:
            f.write(f"Test Case: {r.tc_id} - {r.name}\n")
            f.write(f"  Input:    {r.test_input}\n")
            f.write(f"  Expected: {r.expected}\n")
            f.write(f"  Actual:   {r.actual}\n")
            if r.error:
                f.write(f"  Error:    {r.error}\n")
            f.write(f"  Result:   {'PASS' if r.passed else 'FAIL'}\n\n")
        passed = sum(1 for r in RESULTS if r.passed)
        f.write(f"TOTAL: {passed}/{len(RESULTS)} passed\n")
    print(f"\nText report written to: {REPORT_TXT}")


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(
        description="Start the Node-Map Flask app and run its automated "
                     "verification test suite from the command line.",
    )
    parser.add_argument(
        "--app-dir", default=os.path.dirname(os.path.abspath(__file__)),
        help="Directory containing app.py and the data files "
             "(default: this script's own directory).",
    )
    parser.add_argument(
        "--port", type=int, default=5000,
        help="Port to run the app on for the duration of the tests "
             "(default: 5000). Must be free on this machine.",
    )
    parser.add_argument(
        "--report", default=None,
        help="Path to write the human-readable text report to "
             "(default: verification_report.txt inside --app-dir).",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    global APP_DIR, APP_PORT, BASE_URL, EDGE_FILE, REPORT_TXT
    APP_DIR = os.path.abspath(args.app_dir)
    APP_PORT = args.port
    BASE_URL = f"http://{APP_HOST}:{APP_PORT}"
    EDGE_FILE = os.path.join(APP_DIR, "Graph_Path.txt")
    REPORT_TXT = os.path.abspath(args.report) if args.report else os.path.join(APP_DIR, "verification_report.txt")

    if not os.path.isfile(os.path.join(APP_DIR, "app.py")):
        print(f"ERROR: no app.py found in {APP_DIR}. "
              f"Pass the correct directory with --app-dir.")
        sys.exit(2)

    print(f"Starting Flask app from: {APP_DIR}  (port {APP_PORT})")
    proc = start_server()
    if proc is None:
        print("\nRESULT: FAILURE - application failed to start.")
        sys.exit(2)

    try:
        ref_edges = load_reference_edges(EDGE_FILE)

        public = requests.Session()
        run_safely("TC1", "Normal shortest path", tc1_normal_shortest_path, public, ref_edges)
        run_safely("TC2", "Start node equals end node", tc2_start_equals_end, public, ref_edges)
        run_safely("TC3", "Invalid start node", tc3_invalid_start, public)
        run_safely("TC4", "Invalid destination node", tc4_invalid_end, public)
        run_safely("TC6", "Multiple possible paths", tc6_multiple_paths, public, ref_edges)

        editor = requests.Session()
        login_resp = login(editor)
        if editor.cookies.get("session") is None:
            print("WARNING: login did not appear to set a session cookie; "
                  "TC5 fixture setup may fail.")
        run_safely("TC5", "Disconnected graph / unreachable destination",
                   tc5_unreachable_destination, editor)

        run_safely("TC7", "Editor route rejected for unauthorized user",
                   tc7_unauthorized_editor_access)
        run_safely("TC8", "Public pathfinding without authentication",
                   tc8_public_pathfinding_no_auth)
    finally:
        #stop_server(proc)

        write_report()

        print("\n" + "=" * 72)
        print("VERIFICATION SUMMARY")
        print("=" * 72)
        for r in RESULTS:
            print(f"{r.tc_id:6s} [{'PASS' if r.passed else 'FAIL'}] {r.name}")
        print("=" * 72)

        if all(r.passed for r in RESULTS) and RESULTS:
            print("RESULT: SUCCESS - all test cases passed.")
            sys.exit(0)
        else:
            failed = [r.tc_id for r in RESULTS if not r.passed]
            print(f"RESULT: FAILURE - failed test case(s): {', '.join(failed) or 'none ran'}")
            sys.exit(1)


if __name__ == "__main__":
    main()