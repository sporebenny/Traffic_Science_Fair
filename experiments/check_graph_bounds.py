

import osmnx as ox


# ============================================================
# Graph Boundary Checker
# ============================================================

graph_path = "data/taoyuan_taipei.graphml"

print("=" * 60)
print("Graph Boundary Checker")
print("=" * 60)

print("\n正在載入 Graph...")

G = ox.load_graphml(graph_path)

print("Graph 載入完成")
print(G)

# ============================================================
# 取得所有 Node 座標
# ============================================================

xs = [data["x"] for node, data in G.nodes(data=True)]
ys = [data["y"] for node, data in G.nodes(data=True)]

min_lon = min(xs)
max_lon = max(xs)

min_lat = min(ys)
max_lat = max(ys)

print("\n===== Graph 地理範圍 =====")

print("最西 Longitude:", min_lon)
print("最東 Longitude:", max_lon)

print("最南 Latitude :", min_lat)
print("最北 Latitude :", max_lat)


# ============================================================
# 台北車站
# ============================================================

taipei_lat = 25.0478
taipei_lon = 121.5170

print("\n===== 台北車站 =====")

print("Latitude :", taipei_lat)
print("Longitude:", taipei_lon)


# ============================================================
# 判斷是否在 Graph 範圍內
# ============================================================

inside = (
    min_lon <= taipei_lon <= max_lon
    and
    min_lat <= taipei_lat <= max_lat
)

print("\n===== 判斷結果 =====")

if inside:
    print("台北車站位於 Graph 地理範圍內")
else:
    print("⚠ 台北車站不在 Graph 地理範圍內")

    