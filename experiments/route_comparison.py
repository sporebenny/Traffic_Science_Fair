import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Microsoft JhengHei"]
plt.rcParams["axes.unicode_minus"] = False



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
# Congestion Route Time Model
# ============================================================

def calculate_congestion_time(G, route, congestion_factors):

    total_time = 0

    for i in range(len(route) - 1):

        u = route[i]
        v = route[i + 1]

        edge_data = G.get_edge_data(u, v)

        if edge_data is None:
            continue

        # MultiDiGraph：選擇目前這段道路的最短 Edge
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

        normal_time = calculate_edge_time(
            distance,
            speed
        )

        highway = edge.get(
            "highway",
            "unclassified"
        )

        if isinstance(highway, list):
            highway = highway[0]

        factor = congestion_factors.get(
            highway,
            congestion_factors.get(
                "default",
                1.0
            )
        )

        total_time += (
            normal_time * factor
        )

    return total_time





# ============================================================
# Mission 14 - Step 6.5D-1
# Route Road-Type Profile
# ============================================================

def analyze_route_road_types(G, route):

    road_types = {}

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

        highway = edge.get(
            "highway",
            "unknown"
        )

        if isinstance(highway, list):
            highway = highway[0]

        road_types[highway] = (
            road_types.get(highway, 0) + 1
        )

    return road_types






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


best_routes = {}



# ============================================================
# 差異化道路壅塞係數
# ============================================================

congestion_factors_by_level = {

    "正常": {
        "motorway": 1.00,
        "trunk": 1.00,
        "primary": 1.00,
        "secondary": 1.00,
        "tertiary": 1.00,
        "residential": 1.00,
        "unclassified": 1.00,
        "default": 1.00
    },

    "中度壅塞": {
        "motorway": 1.20,
        "trunk": 1.25,
        "primary": 1.50,
        "secondary": 1.40,
        "tertiary": 1.30,
        "residential": 1.20,
        "unclassified": 1.25,
        "default": 1.25
    },

    "嚴重壅塞": {
        "motorway": 1.40,
        "trunk": 1.50,
        "primary": 1.90,
        "secondary": 1.70,
        "tertiary": 1.50,
        "residential": 1.30,
        "unclassified": 1.40,
        "default": 1.40
    }
}




for congestion_name, factor in congestion_levels.items():

    print(...)

    for route_name, metrics in routes.items():

        congestion_time = (
            metrics["time"] * factor
        )

        print(...)

    best_route = min(
        routes.items(),
        key=lambda item: item[1]["time"] * factor
    )[0]

    best_routes[congestion_name] = best_route

    print(
        "最佳 Route:",
        best_route
    )




# ============================================================
# Step 6.5B
# 差異化壅塞 Route Analysis
# ============================================================

print("\n")
print("=" * 60)
print("差異化壅塞 Route Analysis")
print("=" * 60)



# ============================================================
# Step 6.5C
# Route Switching Threshold Analysis
# ============================================================

print("\n")
print("=" * 60)
print("Route Switching Threshold Analysis")
print("=" * 60)


routes_for_threshold = {

    "Route 1": shortest_distance_route,

    "Route 2": shortest_time_route,

    "Route 3": best_compromise_route

}



base_congestion_factors = {

    "motorway": 1.10,
    "trunk": 1.15,
    "primary": 1.30,
    "secondary": 1.25,
    "tertiary": 1.20,
    "residential": 1.10,
    "unclassified": 1.15,
    "default": 1.15
}



previous_best = None


for severity in [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0]:

    test_factors = {}

    for road_type, base_factor in base_congestion_factors.items():

        test_factors[road_type] = (
            1.0
            + (base_factor - 1.0) * severity
        )


    route_times = {}


    for route_name, route in routes_for_threshold.items():

        route_times[route_name] = calculate_congestion_time(
            G,
            route,
            test_factors
        )


    current_best = min(
        route_times,
        key=route_times.get
    )


    print()
    print(
        "壅塞強度:",
        severity
    )

    print(
        "Route 1:",
        round(route_times["Route 1"], 2),
        "秒"
    )

    print(
        "Route 2:",
        round(route_times["Route 2"], 2),
        "秒"
    )

    print(
        "Route 3:",
        round(route_times["Route 3"], 2),
        "秒"
    )

    print(
        "最佳 Route:",
        current_best
    )


    if (
        previous_best is not None
        and current_best != previous_best
    ):

        print(
            ">>> Route Switching 發生！"
        )

        print(
            "由",
            previous_best,
            "切換為",
            current_best
        )

    previous_best = current_best




for congestion_name, factors in congestion_factors_by_level.items():

    print(
        "\n===== ",
        congestion_name,
        " =====",
        sep=""
    )

    route_congestion_times = {}

    for route_name, route in {
        "Route 1": shortest_distance_route,
        "Route 2": shortest_time_route,
        "Route 3": best_compromise_route
    }.items():

        congestion_time = calculate_congestion_time(
            G,
            route,
            factors
        )

        route_congestion_times[route_name] = congestion_time

        print(
            route_name,
            ":",
            round(congestion_time, 2),
            "秒"
        )

    best_route = min(
        route_congestion_times,
        key=route_congestion_times.get
    )

    print(
        "最佳 Route:",
        best_route
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
# Mission 14 - Step 6.5F-2
# Congestion Decision Summary
# ============================================================

print("\n")
print("=" * 60)
print("Congestion Decision Summary")
print("=" * 60)


congestion_summary_results = {}


for congestion_name, factors in congestion_factors_by_level.items():

    route_times = {}

    for route_name, route in {
        "Route 1": shortest_distance_route,
        "Route 2": shortest_time_route,
        "Route 3": best_compromise_route
    }.items():

        route_times[route_name] = calculate_congestion_time(
            G,
            route,
            factors
        )

    best_route = min(
        route_times,
        key=route_times.get
    )

    congestion_summary_results[congestion_name] = {
        "Route 1": route_times["Route 1"],
        "Route 2": route_times["Route 2"],
        "Route 3": route_times["Route 3"],
        "best": best_route
    }


print()

print(
    "{:<12} {:>12} {:>12} {:>12} {:>12}".format(
        "情境",
        "Route 1",
        "Route 2",
        "Route 3",
        "最佳 Route"
    )
)

print("-" * 62)


for congestion_name, result in congestion_summary_results.items():

    print(
        "{:<12} {:>12.2f} {:>12.2f} {:>12.2f} {:>12}".format(
            congestion_name,
            result["Route 1"],
            result["Route 2"],
            result["Route 3"],
            result["best"]
        )
    )


best_route_set = set(
    result["best"]
    for result in congestion_summary_results.values()
)


print()

if len(best_route_set) == 1:

    print(
        "最佳 Route 是否改變：否"
    )

else:

    print(
        "最佳 Route 是否改變：是"
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
# Mission 14 - Step 6.5F-1
# Route Baseline Summary
# ============================================================

print("\n===== Route Baseline Summary =====")


distance_base = routes[shortest_distance_name]["distance"]

time_base = routes[shortest_time_name]["time"]


for route_name, metrics in routes.items():

    distance_difference = (
        metrics["distance"]
        - distance_base
    )

    time_difference = (
        metrics["time"]
        - time_base
    )

    distance_percentage = (
        distance_difference
        / distance_base
        * 100
    )

    time_percentage = (
        time_difference
        / time_base
        * 100
    )

    print()

    print(
        route_name,
        "相對最短距離 Route:",
        round(
            distance_difference / 1000,
            2
        ),
        "km"
    )

    print(
        route_name,
        "相對最短時間 Route:",
        round(
            time_difference / 60,
            2
        ),
        "分鐘"
    )

    print(
        route_name,
        "距離差異:",
        round(
            distance_percentage,
            2
        ),
        "%"
    )

    print(
        route_name,
        "時間差異:",
        round(
            time_percentage,
            2
        ),
        "%"
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
        6,
        4,
        2
    ],

    route_alpha=0.7,

    node_size=0,
    bgcolor="white",
    show=False,
    close=False
)


ax.set_title(
    "Taoyuan Station → Taipei Main Station\n"
    "Route Comparison"
)

from matplotlib.lines import Line2D

legend_elements = [
    Line2D([0], [0], color="blue", lw=3, label="Route 1 - Shortest Distance"),
    Line2D([0], [0], color="red", lw=3, label="Route 2 - Shortest Time"),
    Line2D([0], [0], color="green", lw=3, label="Route 3 - Compromise")
]



ax.legend(
    handles=legend_elements,
    loc="upper right"
)

# 標記起點與終點
start_x = G.nodes[start_node]["x"]
start_y = G.nodes[start_node]["y"]

end_x = G.nodes[end_node]["x"]
end_y = G.nodes[end_node]["y"]

ax.scatter(
    start_x,
    start_y,
    s=100,
    c="black",
    marker="o",
    zorder=5
)

ax.scatter(
    end_x,
    end_y,
    s=100,
    c="black",
    marker="X",
    zorder=5
)

ax.text(
    start_x,
    start_y,
    "  桃園車站",
    fontsize=10,
    weight="bold"
)

ax.text(
    end_x,
    end_y,
    "  台北車站",
    fontsize=10,
    weight="bold"
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




# ============================================================
# Mission 14 - Step 6.5D-1
# Route Road-Type Profile Analysis
# ============================================================

print("\n")
print("=" * 60)
print("Route Road-Type Profile Analysis")
print("=" * 60)


route_profiles = {

    "Route 1": analyze_route_road_types(
        G,
        shortest_distance_route
    ),

    "Route 2": analyze_route_road_types(
        G,
        shortest_time_route
    ),

    "Route 3": analyze_route_road_types(
        G,
        best_compromise_route
    )

}


for route_name, profile in route_profiles.items():

    print()
    print("===== ", route_name, " =====", sep="")

    total_edges = sum(
        profile.values()
    )

    for road_type, count in sorted(
        profile.items(),
        key=lambda item: item[1],
        reverse=True
    ):

        percentage = (
            count / total_edges * 100
        )

        print(
            road_type,
            ":",
            count,
            "段",
            "(",
            round(percentage, 2),
            "%)"
        )






# ============================================================
# Mission 14 - Step 6.5D-2
# Primary Road Sensitivity Analysis
# ============================================================

print("\n")
print("=" * 60)
print("Primary Road Sensitivity Analysis")
print("=" * 60)


sensitivity_routes = {

    "Route 1": shortest_distance_route,

    "Route 2": shortest_time_route,

    "Route 3": best_compromise_route

}


primary_factors = [
    1.0,
    1.2,
    1.4,
    1.6,
    1.8,
    2.0
]


for primary_factor in primary_factors:

    test_factors = {

        "motorway": 1.0,
        "trunk": 1.0,
        "primary": primary_factor,
        "secondary": 1.0,
        "tertiary": 1.0,
        "residential": 1.0,
        "unclassified": 1.0,
        "default": 1.0

    }


    route_times = {}


    for congestion_name, factors in congestion_factors_by_level.items():

        route_times = {}

        for route_name, route in {
            "Route 1": shortest_distance_route,
            "Route 2": shortest_time_route,
            "Route 3": best_compromise_route
        }.items():

            route_times[route_name] = calculate_congestion_time(
                G,
                route,
                factors
            )
            
    best_route = min(
        route_times,
        key=route_times.get
    )


    print()

    print(
        "Primary 壅塞係數:",
        primary_factor
    )

    print(
        "Route 1:",
        round(
            route_times["Route 1"],
            2
        ),
        "秒"
    )

    print(
        "Route 2:",
        round(
            route_times["Route 2"],
            2
        ),
        "秒"
    )

    print(
        "Route 3:",
        round(
            route_times["Route 3"],
            2
        ),
        "秒"
    )

    print(
        "最佳 Route:",
        best_route
    )



# ============================================================
# Mission 14 - Step 6.5D-2b
# Motorway Road Sensitivity Analysis
# ============================================================

print("\n")
print("=" * 60)
print("Motorway Road Sensitivity Analysis")
print("=" * 60)


motorway_factors = [
    1.0,
    1.2,
    1.4,
    1.6,
    1.8,
    2.0,
    2.2,
    2.4,
    2.6,
    2.8,
    3.0
]


for motorway_factor in motorway_factors:

    test_factors = {

        "motorway": motorway_factor,
        "trunk": 1.0,
        "primary": 1.0,
        "secondary": 1.0,
        "tertiary": 1.0,
        "residential": 1.0,
        "unclassified": 1.0,
        "default": 1.0

    }


    route_times = {}


    for route_name, route in sensitivity_routes.items():

        route_times[route_name] = calculate_congestion_time(
            G,
            route,
            test_factors
        )


    best_route = min(
        route_times,
        key=route_times.get
    )


    print()

    print(
        "Motorway 壅塞係數:",
        motorway_factor
    )

    print(
        "Route 1:",
        round(
            route_times["Route 1"],
            2
        ),
        "秒"
    )

    print(
        "Route 2:",
        round(
            route_times["Route 2"],
            2
        ),
        "秒"
    )

    print(
        "Route 3:",
        round(
            route_times["Route 3"],
            2
        ),
        "秒"
    )

    print(
        "最佳 Route:",
        best_route
    )



# ============================================================
# Mission 14 - Step 6.5D-3
# Route Switching Threshold
# ============================================================

print("\n")
print("=" * 60)
print("Route Switching Threshold Analysis")
print("=" * 60)

threshold_found = False


for motorway_factor in [
    1.20, 1.21, 1.22, 1.23, 1.24,
    1.25, 1.26, 1.27, 1.28, 1.29,
    1.30, 1.31, 1.32, 1.33, 1.34,
    1.35, 1.36, 1.37, 1.38, 1.39,
    1.40
]:

    test_factors = {

        "motorway": motorway_factor,
        "trunk": 1.0,
        "primary": 1.0,
        "secondary": 1.0,
        "tertiary": 1.0,
        "residential": 1.0,
        "unclassified": 1.0,
        "default": 1.0

    }


    route_times = {}


    for route_name, route in sensitivity_routes.items():

        route_times[route_name] = calculate_congestion_time(
            G,
            route,
            test_factors
        )


    best_route = min(
        route_times,
        key=route_times.get
    )


    print(
        "Motorway:",
        round(motorway_factor, 2),
        "|",
        "R1:",
        round(route_times["Route 1"], 2),
        "|",
        "R2:",
        round(route_times["Route 2"], 2),
        "|",
        "R3:",
        round(route_times["Route 3"], 2),
        "|",
        "最佳:",
        best_route
    )


    if best_route != "Route 2":

        print()
        print(
            ">>> Route Switching Threshold:",
            round(motorway_factor, 2)
        )

        threshold_found = True

        break


if not threshold_found:

    print()
    print(
        "1.20～1.40 範圍內沒有發生 Route Switching"
    )




# ============================================================
# Mission 14 - Step 6.5E
# Route Switching Result Validation
# ============================================================

print("\n")
print("=" * 60)
print("Route Switching Result Validation")
print("=" * 60)


validation_factors = {

    "motorway": 1.29,
    "trunk": 1.0,
    "primary": 1.0,
    "secondary": 1.0,
    "tertiary": 1.0,
    "residential": 1.0,
    "unclassified": 1.0,
    "default": 1.0

}


route_times_before = {}

for route_name, route in sensitivity_routes.items():

    route_times_before[route_name] = calculate_congestion_time(
        G,
        route,
        validation_factors
    )


best_before = min(
    route_times_before,
    key=route_times_before.get
)


print()
print("===== 切換前 =====")
print("Motorway 壅塞係數: 1.29")

print(
    "Route 1:",
    round(route_times_before["Route 1"], 2),
    "秒"
)

print(
    "Route 2:",
    round(route_times_before["Route 2"], 2),
    "秒"
)

print(
    "Route 3:",
    round(route_times_before["Route 3"], 2),
    "秒"
)

print(
    "最佳 Route:",
    best_before
)


validation_factors["motorway"] = 1.30


route_times_after = {}

for route_name, route in sensitivity_routes.items():

    route_times_after[route_name] = calculate_congestion_time(
        G,
        route,
        validation_factors
    )


best_after = min(
    route_times_after,
    key=route_times_after.get
)


print()
print("===== 切換後 =====")
print("Motorway 壅塞係數: 1.30")

print(
    "Route 1:",
    round(route_times_after["Route 1"], 2),
    "秒"
)

print(
    "Route 2:",
    round(route_times_after["Route 2"], 2),
    "秒"
)

print(
    "Route 3:",
    round(route_times_after["Route 3"], 2),
    "秒"
)

print(
    "最佳 Route:",
    best_after
)


print()

if best_before != best_after:

    print(
        "✅ Route Switching 驗證成功"
    )

    print(
        "Route:",
        best_before,
        "→",
        best_after
    )

else:

    print(
        "❌ Route Switching 驗證失敗"
    )


# ============================================================
# Mission 14 - Step 6.5F-3
# Route Switching Threshold Summary
# ============================================================

print("\n")
print("=" * 60)
print("Route Switching Threshold Summary")
print("=" * 60)


switch_before = route_times_before

switch_after = route_times_after


print()
print("===== 切換前 =====")

print(
    "Motorway 壅塞係數:",
    1.29
)

print(
    "Route 2:",
    round(
        switch_before["Route 2"],
        2
    ),
    "秒"
)

print(
    "Route 3:",
    round(
        switch_before["Route 3"],
        2
    ),
    "秒"
)

print(
    "最佳 Route:",
    best_before
)


print()
print("===== 切換後 =====")

print(
    "Motorway 壅塞係數:",
    1.30
)

print(
    "Route 2:",
    round(
        switch_after["Route 2"],
        2
    ),
    "秒"
)

print(
    "Route 3:",
    round(
        switch_after["Route 3"],
        2
    ),
    "秒"
)

print(
    "最佳 Route:",
    best_after
)


before_difference = (
    switch_before["Route 3"]
    - switch_before["Route 2"]
)

after_difference = (
    switch_after["Route 2"]
    - switch_after["Route 3"]
)


print()

print(
    "切換前 Route 2 領先:",
    round(
        before_difference,
        2
    ),
    "秒"
)

print(
    "切換後 Route 3 領先:",
    round(
        after_difference,
        2
    ),
    "秒"
)


print()

if best_before != best_after:

    print(
        "✅ 最佳 Route 發生切換"
    )

    print(
        "Route:",
        best_before,
        "→",
        best_after
    )

else:

    print(
        "❌ 最佳 Route 未發生切換"
    )



