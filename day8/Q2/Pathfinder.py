import heapq
from collections import defaultdict

graph = defaultdict(list)

def build_graph(data):
    graph = defaultdict(list)
    for a, b, dist in data:
        graph[a].append((b, dist))
        graph[b].append((a, dist))
    return graph

def dijkstra(start, destination):
    dist = {start: 0}
    prev = {start: None}
    visited = set()
    pq = [(0, start)]
 
    while pq:
        d, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)
        if u == destination:
            break
        for v, w in graph[u]:
            nd = d + w
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
 
    if destination not in dist:
        return None, None
 
    path = []
    node = destination
    while node is not None:
        path.append(node)
        node = prev[node]
    path.reverse()
    return path, dist[destination]


def craft_message(starting, destination, path, distance):
    message = (
        f"Start node: {starting}\n"
        f"End node: {destination}\n"
        f"Shortest path:\n{" -> ".join(map(str, path))}\n"
        f"Total distance:\n{distance}\n"
    )
    return message


def find_shortest_distance(graph_data, starting, destination):
    global graph
    graph = build_graph(graph_data)

    if starting not in graph:
        return f"Start node: {starting} is invalid."
    if destination not in graph:
        return f"End node: {destination} is invalid."
    
    path, distance = dijkstra(starting, destination)

    if path != None:
        return path, distance, craft_message(starting, destination, path, distance)
    else:
        return "No Path Exists"
    