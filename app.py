from flask import Flask, render_template, jsonify
import osmnx as ox


app = Flask(__name__)


# ============================================================
# 載入 Graph
# ============================================================

graph_path = "data/taoyuan_taipei.graphml"

G = ox.load_graphml(graph_path)


# ============================================================
# 載入三條 Route
# ============================================================

from experiments.route_comparison import (
    shortest_distance_route,
    shortest_time_route,
    best_compromise_route
)


# ============================================================
# Route → OSM Edge Geometry → Leaflet 座標
# ============================================================

def route_to_coordinates(route, weight):

    coordinates = []

    for i in range(len(route) - 1):

        u = route[i]
        v = route[i + 1]

        edge_data = G.get_edge_data(u, v)

        if edge_data is None:
            continue

        # ----------------------------------------------------
        # MultiDiGraph 可能存在多條 u → v Edge
        # 選擇與該 Route 使用的 weight 相符的最佳 Edge
        # ----------------------------------------------------

        edge = min(
            edge_data.values(),
            key=lambda data: data.get(
                weight,
                float("inf")
            )
        )

        # ----------------------------------------------------
        # 如果 OSM Edge 有 geometry
        # 使用真正道路幾何
        # ----------------------------------------------------

        geometry = edge.get("geometry")

        if geometry is not None:

            edge_coordinates = []

            for x, y in geometry.coords:

                edge_coordinates.append([
                    float(y),
                    float(x)
                ])

            # 避免相鄰 Edge 重複加入同一個 Node
            if coordinates:
                edge_coordinates = edge_coordinates[1:]

            coordinates.extend(edge_coordinates)

        # ----------------------------------------------------
        # 如果沒有 geometry
        # 使用 Node 座標作為 fallback
        # ----------------------------------------------------

        else:

            x = float(G.nodes[v]["x"])
            y = float(G.nodes[v]["y"])

            if not coordinates:

                start_x = float(G.nodes[u]["x"])
                start_y = float(G.nodes[u]["y"])

                coordinates.append([
                    start_y,
                    start_x
                ])

            coordinates.append([
                y,
                x
            ])

    return coordinates


# ============================================================
# 首頁
# ============================================================

@app.route("/")
def home():

    return render_template("index.html")


# ============================================================
# Route API
# ============================================================

@app.route("/api/routes")
def routes():

    return jsonify({

        # Route 1
        # 最短距離
        "route1": route_to_coordinates(
            shortest_distance_route,
            "length"
        ),

        # Route 2
        # 最短時間
        "route2": route_to_coordinates(
            shortest_time_route,
            "travel_time"
        ),

        # Route 3
        # 折衷 Route
        "route3": route_to_coordinates(
            best_compromise_route,
            "compromise_cost"
        )

    })


# ============================================================
# 啟動 Flask
# ============================================================

if __name__ == "__main__":

    app.run(debug=True)


    