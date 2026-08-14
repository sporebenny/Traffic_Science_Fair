import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt



def analyze_route(G, route):
    """
    分析一條 Route 的：
    1. 總距離
    2. 正常旅行時間
    3. 經過的道路數量
    """

    total_distance = 0
    total_time = 0

    for u, v in zip(route[:-1], route[1:]):

        edge_data = G.get_edge_data(u, v)

        # MultiDiGraph 可能存在多條 Edge
        edge = min(
            edge_data.values(),
            key=lambda data: data.get("length", float("inf"))
        )

        distance = float(edge.get("length", 0))

        speed = edge.get("maxspeed", 40)

        # maxspeed 可能是 list
        if isinstance(speed, list):
            speed = speed[0]

        # 有些 OSM 資料可能不是純數字
        try:
            speed = float(speed)
        except (ValueError, TypeError):
            speed = 40.0

        speed_mps = speed * 1000 / 3600

        if speed_mps > 0:
            time = distance / speed_mps
        else:
            time = 0

        total_distance += distance
        total_time += time

    return {
        "distance": total_distance,
        "time": total_time,
        "nodes": len(route)
    }



# ============================================================
# 桃園車站 → 台北車站 Route Comparison
# ============================================================

print("=" * 60)
print("桃園車站 → 台北車站 Route Comparison")
print("=" * 60)


# ============================================================
# Graph
# ============================================================

graph_path = "data/taoyuan_taipei.graphml"

print("\n正在載入 Graph...")

G = ox.load_graphml(graph_path)

print("Graph 載入完成")
print(G)
print("Nodes:", len(G.nodes))
print("Edges:", len(G.edges))


# ============================================================
# Station Information
# ============================================================

start_name = "桃園車站"
end_name = "台北車站"

start_lat = 24.9896
start_lon = 121.3136

end_lat = 25.0478
end_lon = 121.5170


# ============================================================
# Node ID
# ============================================================

start_node = 9245588603
end_node = 662312865


print("\n" + "=" * 60)
print("Route 起終點")
print("=" * 60)

print("\n起點")
print("名稱:", start_name)
print("Latitude:", start_lat)
print("Longitude:", start_lon)
print("Node:", start_node)

print("\n終點")
print("名稱:", end_name)
print("Latitude:", end_lat)
print("Longitude:", end_lon)
print("Node:", end_node)


# ============================================================
# Travel Time
# ============================================================

print("\n正在建立 Travel Time...")


def parse_speed(speed):
    """
    將 OSM maxspeed 轉成 km/h 數值。
    """

    if speed is None:
        return None

    if isinstance(speed, list):
        speed = speed[0]

    if isinstance(speed, str):

        speed = speed.replace("km/h", "")
        speed = speed.strip()

        try:
            return float(speed)

        except ValueError:
            return None

    try:
        return float(speed)

    except (TypeError, ValueError):
        return None


def calculate_edge_time(distance, speed):
    """
    distance: 公尺
    speed: km/h

    回傳：
    秒
    """

    if speed is None or speed <= 0:
        speed = 40.0

    speed_mps = speed * 1000 / 3600

    return distance / speed_mps


# ============================================================
# 將每條 Edge 加入 travel_time
# ============================================================

for u, v, key, data in G.edges(keys=True, data=True):

    distance = float(data.get("length", 0))

    speed = parse_speed(
        data.get("maxspeed")
    )

    travel_time = calculate_edge_time(
        distance,
        speed
    )

    data["speed_kmh"] = speed if speed else 40.0

    data["travel_time"] = travel_time


print("Travel Time 建立完成")


# ============================================================
# Route 計算
# ============================================================

print("\n正在計算最短距離 Route...")

shortest_distance_route = nx.shortest_path(
    G,
    source=start_node,
    target=end_node,
    weight="length"
)


print("正在計算最短時間 Route...")

shortest_time_route = nx.shortest_path(
    G,
    source=start_node,
    target=end_node,
    weight="travel_time"
)


# ============================================================
# Route Metrics
# ============================================================

def calculate_route_metrics(G, route):
    """
    計算一條 Route：

    1. 總距離
    2. 正常旅行時間
    3. 道路段數
    """

    total_distance = 0
    total_time = 0

    edge_count = 0

    for i in range(len(route) - 1):

        u = route[i]
        v = route[i + 1]

        edge_data = G.get_edge_data(u, v)

        if edge_data is None:
            continue

        # MultiDiGraph
        edge = min(
            edge_data.values(),
            key=lambda x: x.get("length", float("inf"))
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
# Calculate Route 1 / Route 2
# ============================================================

route1_metrics = calculate_route_metrics(
    G,
    shortest_distance_route
)

route2_metrics = calculate_route_metrics(
    G,
    shortest_time_route
)


# ============================================================
# 建立折衷 Route
# ============================================================

print("正在建立折衷 Route...")


# ============================================================
# 取得兩條基準 Route
# ============================================================

distance_max = max(
    route1_metrics["distance"],
    route2_metrics["distance"]
)

time_max = max(
    route1_metrics["time"],
    route2_metrics["time"]
)



# ============================================================
# 建立綜合成本
#
# 50% 距離
# 50% 時間
# ============================================================

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
    )

    time_score = (
        travel_time / time_max
    )

    compromise_cost = (
        0.5 * distance_score
        +
        0.5 * time_score
    )

    data["compromise_cost"] = compromise_cost


# ============================================================
# 使用綜合成本尋找折衷 Route
# ============================================================

best_compromise_route = nx.shortest_path(
    G,
    source=start_node,
    target=end_node,
    weight="compromise_cost"
)


route3_metrics = calculate_route_metrics(
    G,
    best_compromise_route
)


# 計算折衷 Route 的成本
best_compromise_score = 0

for i in range(
    len(best_compromise_route) - 1
):

    u = best_compromise_route[i]
    v = best_compromise_route[i + 1]

    edge_data = G.get_edge_data(u, v)

    edge = min(
        edge_data.values(),
        key=lambda x: x.get(
            "compromise_cost",
            float("inf")
        )
    )

    best_compromise_score += (
        edge.get(
            "compromise_cost",
            0
        )
    )



# 如果沒有找到候選 Route
if best_compromise_route is None:

    best_compromise_route = shortest_distance_route


route3_metrics = calculate_route_metrics(
    G,
    best_compromise_route
)


# ============================================================
# Route Analysis
# ============================================================

print("\n")
print("=" * 60)
print("Route Analysis")
print("=" * 60)


print("\n===== Route 1：最短距離 =====")

print(
    "Node 數量:",
    route1_metrics["nodes"]
)

print(
    "道路段數:",
    route1_metrics["edges"]
)

print(
    "總距離:",
    round(
        route1_metrics["distance"],
        2
    ),
    "m"
)

print(
    "總時間:",
    round(
        route1_metrics["time"],
        2
    ),
    "秒"
)


print("\n===== Route 2：最短時間 =====")

print(
    "Node 數量:",
    route2_metrics["nodes"]
)

print(
    "道路段數:",
    route2_metrics["edges"]
)

print(
    "總距離:",
    round(
        route2_metrics["distance"],
        2
    ),
    "m"
)

print(
    "總時間:",
    round(
        route2_metrics["time"],
        2
    ),
    "秒"
)


print("\n===== Route 3：折衷 Route =====")

print(
    "Node 數量:",
    route3_metrics["nodes"]
)

print(
    "道路段數:",
    route3_metrics["edges"]
)

print(
    "總距離:",
    round(
        route3_metrics["distance"],
        2
    ),
    "m"
)

print(
    "總時間:",
    round(
        route3_metrics["time"],
        2
    ),
    "秒"
)

print(
    "折衷成本:",
    round(
        best_compromise_score,
        4
    )
)


# ============================================================
# Route Nodes
# ============================================================

print("\n===== Route 1 Nodes =====")

print(shortest_distance_route)


print("\n===== Route 2 Nodes =====")

print(shortest_time_route)


print("\n===== Route 3 Nodes =====")

print(best_compromise_route)


# ============================================================
# Congestion Analysis
# ============================================================

print("\n")
print("=" * 60)
print("Congestion Analysis")
print("=" * 60)


congestion_levels = {

    "正常": 1.0,

    "中度壅塞": 1.5,

    "嚴重壅塞": 2.0

}


routes = {

    "Route 1": route1_metrics,

    "Route 2": route2_metrics,

    "Route 3": route3_metrics

}


for congestion_name, factor in congestion_levels.items():

    print(
        "\n===== ",
        congestion_name,
        " =====",
        sep=""
    )

    for route_name, metrics in routes.items():

        congestion_time = (
            metrics["time"] * factor
        )

        print(
            route_name,
            ":",
            round(
                congestion_time,
                2
            ),
            "秒"
        )


# ============================================================
# Route Comparison Summary
# ============================================================

print("\n")
print("=" * 60)
print("三條 Route 最終比較")
print("=" * 60)


print(
    "\n{:<12} {:>15} {:>15}".format(
        "Route",
        "距離(m)",
        "正常時間(s)"
    )
)


print("-" * 45)


for route_name, metrics in routes.items():

    print(
        "{:<12} {:>15.2f} {:>15.2f}".format(
            route_name,
            metrics["distance"],
            metrics["time"]
        )
    )


# ============================================================
# 找出各項最佳 Route
# ============================================================

shortest_distance_name = min(
    routes,
    key=lambda r: routes[r]["distance"]
)

shortest_time_name = min(
    routes,
    key=lambda r: routes[r]["time"]
)


print("\n===== 最佳 Route 判斷 =====")

print(
    "最短距離 Route:",
    shortest_distance_name
)

print(
    "最短時間 Route:",
    shortest_time_name
)


# ============================================================
# Route Visualization
# ============================================================

print("\n正在繪製 Route...")


fig, ax = ox.plot_graph_routes(
    G,
    routes=[
        shortest_distance_route,
        shortest_time_route,
        best_compromise_route
    ],
    route_colors=[
        "blue",
        "red",
        "green"
    ],
    route_linewidths=[
        3,
        3,
        3
    ],
    node_size=0,
    bgcolor="white",
    show=False,
    close=False
)


ax.set_title(
    "Taoyuan Station → Taipei Main Station\n"
    "Route Comparison"
)


plt.show()


print("Route 圖繪製完成")


# ============================================================
# Finish
# ============================================================

print("\n")
print("=" * 60)
print("Route Comparison 完成")
print("=" * 60)



