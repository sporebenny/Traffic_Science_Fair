

import osmnx as ox


print("Graph Visualizer 啟動")


# =========================
# 讀取 Graph
# =========================

graph_path = "data/taoyuan_taipei.graphml"


G = ox.load_graphml(graph_path)


print("Graph 載入完成")

print(G)



# =========================
# 繪製道路網
# =========================

print("開始繪圖...")


fig, ax = ox.plot_graph(
    G,
    node_size=5,
    edge_color="black"
)


print("繪圖完成")