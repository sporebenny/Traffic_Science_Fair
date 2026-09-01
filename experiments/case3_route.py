



# ============================================================
# Mission 14 - Case 3
# 桃園車站 → 信義計畫區
# ============================================================

import osmnx as ox
import networkx as nx


# ============================================================
# Graph
# ============================================================

GRAPH_PATH = "data/taoyuan_taipei.graphml"

print("=" * 60)
print("Mission 14 - Case 3")
print("桃園車站 → 信義計畫區")
print("=" * 60)

print("\n正在載入 Graph...")

G = ox.load_graphml(GRAPH_PATH)

print("Graph 載入完成")
print(G)
print("Nodes:", len(G.nodes))
print("Edges:", len(G.edges))


# ============================================================
# Speed / Travel Time
# ============================================================

def parse_speed(speed):

    if speed is None:
        return None

    if isinstance(speed, list):
        speed = speed[0]

    if isinstance(speed, str):

        speed = speed.replace("km/h", "").strip()

        try:
            return float(speed)

        except ValueError:
            return None

    try:
        return float(speed)

    except (TypeError, ValueError):
        return None


def calculate_edge_time(distance, speed):

    if speed is None or speed <= 0:
        speed = 40.0

    speed_mps = speed * 1000 / 3600

    return distance / speed_mps


# ============================================================
# 建立 Travel Time
# ============================================================

print("\n正在建立 Travel Time...")

for u, v, key, data in G.edges(
    keys=True,
    data=True
):

    distance = float(
        data.get("length", 0)
    )

    speed = parse_speed(
        data.get("maxspeed")
    )

    data["travel_time"] = calculate_edge_time(
        distance,
        speed
    )


print("Travel Time 建立完成")


# ============================================================
# Route Metrics
# ============================================================

def calculate_route_metrics(G, route):

    total_distance = 0
    total_time = 0
    edge_count = 0

    for i in range(len(route) - 1):

        u = route[i]
        v = route[i + 1]

        edge_data = G.get_edge_data(u, v)

        if edge_data is None:
            continue

        edge = min(
            edge_data.values(),
            key=lambda x: x.get(
                "length",
                float("inf")
            )
        )

        distance = float(
            edge.get("length", 0)
        )

        speed = parse_speed(
            edge.get("maxspeed")
        )

        travel_time = calculate_edge_time(
            distance,
            speed
        )

        total_distance += distance
        total_time += travel_time
        edge_count += 1

    return {
        "distance": total_distance,
        "time": total_time,
        "edges": edge_count,
        "nodes": len(route)
    }


# ============================================================
# Route 3 - Compromise
# ============================================================

def calculate_compromise_route(
    G,
    start_node,
    end_node,
    distance_max,
    time_max
):

    for u, v, key, data in G.edges(
        keys=True,
        data=True
    ):

        distance = float(
            data.get("length", 0)
        )

        travel_time = float(
            data.get("travel_time", 0)
        )

        distance_score = (
            distance / distance_max
            if distance_max > 0
            else 0
        )

        time_score = (
            travel_time / time_max
            if time_max > 0
            else 0
        )

        data["compromise_cost"] = (
            0.5 * distance_score
            +
            0.5 * time_score
        )

    return nx.shortest_path(
        G,
        source=start_node,
        target=end_node,
        weight="compromise_cost"
    )


# ============================================================
# Case 2 起終點
# ============================================================

start_name = "桃園車站"
start_lat = 24.9896
start_lon = 121.3136

end_name = "信義計畫區（台北101）"
end_lat = 25.0331
end_lon = 121.5490


start_node = ox.distance.nearest_nodes(
    G,
    X=start_lon,
    Y=start_lat
)

end_node = ox.distance.nearest_nodes(
    G,
    X=end_lon,
    Y=end_lat
)


print("\n起點")
print(
    start_name,
    "→ Node:",
    start_node
)

print("\n終點")
print(
    end_name,
    "→ Node:",
    end_node
)


# ============================================================
# Route 1
# ============================================================

print("\n正在計算 Route 1...")

route1 = nx.shortest_path(
    G,
    source=start_node,
    target=end_node,
    weight="length",
    method="dijkstra"
)


# ============================================================
# Route 2
# ============================================================

print("正在計算 Route 2...")

route2 = nx.shortest_path(
    G,
    source=start_node,
    target=end_node,
    weight="travel_time",
    method="dijkstra"
)


# ============================================================
# Route 1 / Route 2 Metrics
# ============================================================

route1_metrics = calculate_route_metrics(
    G,
    route1
)

route2_metrics = calculate_route_metrics(
    G,
    route2
)


# ============================================================
# Route 3
# ============================================================

print("正在計算 Route 3...")

distance_max = max(
    route1_metrics["distance"],
    route2_metrics["distance"]
)

time_max = max(
    route1_metrics["time"],
    route2_metrics["time"]
)

route3 = calculate_compromise_route(
    G,
    start_node,
    end_node,
    distance_max,
    time_max
)

route3_metrics = calculate_route_metrics(
    G,
    route3
)


# ============================================================
# 結果
# ============================================================

route_times = {

    "Route 1": route1_metrics["time"],
    "Route 2": route2_metrics["time"],
    "Route 3": route3_metrics["time"]

}

best_route = min(
    route_times,
    key=route_times.get
)


print("\n")
print("=" * 60)
print("Case 2 Route Analysis")
print("=" * 60)


print("\nRoute 1：最短距離")

print(
    "距離:",
    round(
        route1_metrics["distance"],
        2
    ),
    "m"
)

print(
    "時間:",
    round(
        route1_metrics["time"],
        2
    ),
    "秒"
)


print("\nRoute 2：最短時間")

print(
    "距離:",
    round(
        route2_metrics["distance"],
        2
    ),
    "m"
)

print(
    "時間:",
    round(
        route2_metrics["time"],
        2
    ),
    "秒"
)


print("\nRoute 3：折衷")

print(
    "距離:",
    round(
        route3_metrics["distance"],
        2
    ),
    "m"
)

print(
    "時間:",
    round(
        route3_metrics["time"],
        2
    ),
    "秒"
)


print(
    "\n正常情況最佳 Route:",
    best_route
)


print("\n")
print("=" * 60)
print("Case 2 Route Runner 完成")
print("=" * 60)

