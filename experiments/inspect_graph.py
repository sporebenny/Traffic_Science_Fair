

import osmnx as ox


# ==========================
# 1. 下載道路 Graph
# ==========================

place_name = "Taoyuan District, Taoyuan, Taiwan"

print("重新建立道路模型...")

G = ox.graph_from_place(
    place_name,
    network_type="drive"
)


# ==========================
# 2. 基本資訊
# ==========================

print("\n===== Graph 基本資訊 =====")

print(G)

print("Node 數量：", len(G.nodes))
print("Edge 數量：", len(G.edges))


# ==========================
# 3. 查看一個 Node
# ==========================

print("\n===== 第一個 Node =====")

first_node = list(G.nodes)[0]

print(first_node)

print(
    G.nodes[first_node]
)


# ==========================
# 4. 查看一條道路 Edge
# ==========================

print("\n===== 第一條道路 Edge =====")


first_edge = list(G.edges(keys=True))[0]

print(first_edge)


print(
    G.edges[first_edge]
)