



# ============================================================
# Multi-Case Definitions
# ============================================================

cases = [

    {
        "name": "Case 1",
        "purpose": "跨縣市移動",

        "start_name": "桃園車站",
        "start_lat": 24.9896,
        "start_lon": 121.3136,

        "end_name": "台北車站",
        "end_lat": 25.0478,
        "end_lon": 121.5170
    },

    {
        "name": "Case 2",
        "purpose": "觀光旅遊",

        "start_name": "桃園車站",
        "start_lat": 24.9896,
        "start_lon": 121.3136,

        "end_name": "西門町",
        "end_lat": 25.0420,
        "end_lon": 121.5081
    },

    {
        "name": "Case 3",
        "purpose": "商業都市核心",

        "start_name": "桃園車站",
        "start_lat": 24.9896,
        "start_lon": 121.3136,

        "end_name": "信義計畫區",
        "end_lat": 25.0330,
        "end_lon": 121.5654
    }

]


# ============================================================
# Multi-Case Congestion Factors
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


# ============================================================
# Multi-Case Analysis
# ============================================================

all_case_results = []


for case in cases:

    print("\n")
    print("=" * 60)
    print(
        case["name"],
        "-",
        case["purpose"]
    )
    print("=" * 60)


    # ========================================================
    # 找最近 Node
    # ========================================================

    start_node = ox.distance.nearest_nodes(
        G,
        X=case["start_lon"],
        Y=case["start_lat"]
    )

    end_node = ox.distance.nearest_nodes(
        G,
        X=case["end_lon"],
        Y=case["end_lat"]
    )


    print("\n起點")
    print(
        case["start_name"],
        "→ Node:",
        start_node
    )

    print("\n終點")
    print(
        case["end_name"],
        "→ Node:",
        end_node
    )


    # ========================================================
    # Route 1：最短距離
    # ========================================================

    print("\n正在計算 Route 1...")

    route1 = nx.shortest_path(
        G,
        source=start_node,
        target=end_node,
        weight="length",
        method="dijkstra"
    )


    # ========================================================
    # Route 2：最短時間
    # ========================================================

    print("正在計算 Route 2...")

    route2 = nx.shortest_path(
        G,
        source=start_node,
        target=end_node,
        weight="travel_time",
        method="dijkstra"
    )


    # ========================================================
    # Route 1 / Route 2 Metrics
    # ========================================================

    route1_metrics = calculate_route_metrics(
        G,
        route1
    )

    route2_metrics = calculate_route_metrics(
        G,
        route2
    )


    # ========================================================
    # Route 3：折衷
    # ========================================================

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


    # ========================================================
    # 正常情況最佳 Route
    # ========================================================

    normal_route_times = {

        "Route 1": route1_metrics["time"],
        "Route 2": route2_metrics["time"],
        "Route 3": route3_metrics["time"]

    }


    best_route = min(
        normal_route_times,
        key=normal_route_times.get
    )


    # ========================================================
    # Route Analysis
    # ========================================================

    print("\n===== Route Analysis =====")


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


    # ========================================================
    # Congestion Analysis
    # ========================================================

    congestion_results = {}


    for congestion_name, factors in (
        congestion_factors_by_level.items()
    ):

        route_times = {}


        for route_name, route in {

            "Route 1": route1,
            "Route 2": route2,
            "Route 3": route3

        }.items():

            congestion_time = calculate_congestion_time(
                G,
                route,
                factors
            )

            route_times[route_name] = (
                congestion_time
            )


        congestion_best_route = min(
            route_times,
            key=route_times.get
        )


        congestion_results[congestion_name] = {

            "Route 1": route_times["Route 1"],
            "Route 2": route_times["Route 2"],
            "Route 3": route_times["Route 3"],
            "best": congestion_best_route

        }


        print()

        print(
            "===== ",
            congestion_name,
            " =====",
            sep=""
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
            congestion_best_route
        )


    # ========================================================
    # 儲存本案例結果
    # ========================================================

    all_case_results.append({

        "case": case["name"],
        "purpose": case["purpose"],

        "start_name": case["start_name"],
        "end_name": case["end_name"],

        "start_node": start_node,
        "end_node": end_node,

        "route1": route1_metrics,
        "route2": route2_metrics,
        "route3": route3_metrics,

        "best_route": best_route,

        "congestion_results": congestion_results

    })





