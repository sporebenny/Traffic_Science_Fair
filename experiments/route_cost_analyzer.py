

import osmnx as ox




# ==========================
# Road Cost Model
# ==========================


def calculate_time(distance, speed, congestion_factor=1.0):

    """
    計算道路旅行時間

    distance:
        公尺

    speed:
        km/h

    congestion_factor:
        壅塞倍率

    """

    speed_mps = speed * 1000 / 3600


    base_time = distance / speed_mps


    travel_time = base_time * congestion_factor


    return travel_time






print("Route Cost Analyzer 啟動")


# ==========================
# 讀取 Graph
# ==========================

graph_path = "data/taoyuan.graphml"

G = ox.load_graphml(graph_path)


print("Graph 載入完成")

print(G)



# ============================
# 尋找最短路線
# ============================
start_node = 31365361

end_node = 1907143368

import networkx as nx

route = nx.shortest_path(
    G,
    source=start_node,
    target=end_node,
    weight="length"
)

print()
print("===== Route =====")
print(route)



# ============================
# 計算 Route 總距離
# ============================


total_distance = 0


for i in range(len(route)-1):

    start = route[i]

    end = route[i+1]


    edge = G.get_edge_data(start, end)


    distance = edge[0]["length"]


    total_distance += distance



print()

print("===== Distance Analysis =====")

print("總距離:", total_distance, "m")




# ============================
# 計算 Route Travel Time
# ============================

total_time = 0


for i in range(len(route)-1):

    start = route[i]

    end = route[i+1]


    edge = G.get_edge_data(start, end)


    road = edge[0]


    distance = road["length"]


    speed = road["maxspeed"]


    # 處理速限格式
    if isinstance(speed, list):
        speed = speed[0]


    speed = float(speed)


    time = calculate_time(
        distance,
        speed,
        congestion_factor=1.0
    )


    total_time += time



# ============================
# Congestion Simulation
# ============================

print()

print("===== Congestion Simulation =====")


for factor in [1.0, 1.5, 2.0]:

    congestion_time = calculate_time(
        total_distance,
        speed,
        congestion_factor=factor
    )


    print()

    print("壅塞係數:", factor)

    print(
        "旅行時間:",
        round(congestion_time, 2),
        "秒"
    )



print()

print("===== Travel Time Analysis =====")

print("總旅行時間:", total_time, "秒")

# ==========================
# 設定測試起點與終點
# ==========================




print("\n===== Route 設定 =====")

print("起點 Node:", start_node)

print("終點 Node:", end_node)


# ==========================
# 查詢起點到終點道路
# ==========================

print("\n===== Edge 查詢 =====")


if G.has_edge(start_node, end_node):

    edge_data = G.get_edge_data(start_node, end_node)

    print("找到道路連接")

    print(edge_data)

else:

    print("沒有直接道路連接")