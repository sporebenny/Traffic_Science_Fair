

import osmnx as ox


place_name = "Taoyuan District, Taoyuan, Taiwan"


print("===================================")
print("      Graph Explorer v1")
print("===================================")


print("\n開始建立道路模型...")


G = ox.graph_from_place(
    place_name,
    network_type="drive"
)


print("完成！")


print("\n目前研究區域：")
print(place_name)


# =====================================
# Graph 基本資訊
# =====================================

print("\n===== Graph 基本資訊 =====")

print("Node 數量：", len(G.nodes))

print("Edge 數量：", len(G.edges))



# =====================================
# 第一個 Node
# =====================================

print("\n===== 第一個 Node =====")

# 取得第一個 Node 的 ID
first_node = list(G.nodes)[0]

print("Node ID：", first_node)

# 取得這個 Node 的資料
node_data = G.nodes[first_node]

print("經度 (x)：", node_data["x"])
print("緯度 (y)：", node_data["y"])


# =====================================
# 第一條 Edge
# =====================================

print("\n===== 第一條 Edge =====")

# 取得第一條 Edge
u, v, key = list(G.edges(keys=True))[0]

print("起點 Node：", u)
print("終點 Node：", v)

# 取得 Edge 的所有資料
edge_data = G.get_edge_data(u, v, key)

print("\nEdge 所有欄位：")
print(edge_data)
