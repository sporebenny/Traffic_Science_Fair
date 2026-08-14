

import osmnx as ox


# ============================================================
# Station Node Finder
# 尋找桃園車站 / 台北車站附近的道路 Node
# ============================================================


print("=" * 60)
print("Station Node Finder")
print("=" * 60)


# ============================================================
# 1. 載入桃園－台北 Graph
# ============================================================

graph_path = "data/taoyuan_taipei.graphml"

print("\n正在載入 Graph...")

G = ox.load_graphml(graph_path)

print("Graph 載入完成")
print(G)

print("Nodes:", len(G.nodes))
print("Edges:", len(G.edges))


# ============================================================
# 2. 車站座標
# ============================================================

stations = {

    "桃園車站": {
        "lat": 24.9896,
        "lon": 121.3136
    },

    "台北車站": {
        "lat": 25.0478,
        "lon": 121.5170
    }

}


# ============================================================
# 3. 尋找最近 Node
# ============================================================

for name, station in stations.items():

    print("\n" + "=" * 60)
    print(name)
    print("=" * 60)

    node = ox.distance.nearest_nodes(
        G,
        X=station["lon"],
        Y=station["lat"]
    )

    node_data = G.nodes[node]

    print("指定座標")
    print("Latitude :", station["lat"])
    print("Longitude:", station["lon"])

    print("\n找到的 Node")
    print("Node ID  :", node)

    print("Node 座標")
    print("Latitude :", node_data["y"])
    print("Longitude:", node_data["x"])

    