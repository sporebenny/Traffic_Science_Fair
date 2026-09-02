from flask import Flask, render_template, jsonify, request
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
# Case 2：桃園車站 → 西門町
# ============================================================

from experiments.case2_route import (
    route1 as case2_route1,
    route2 as case2_route2,
    route3 as case2_route3
)

# ============================================================
# Case 3：桃園車站 → 信義計畫區
# ============================================================

from experiments.case3_route import (
    route1 as case3_route1,
    route2 as case3_route2,
    route3 as case3_route3
)





# ============================================================
# Route → OSM Edge Geometry → Leaflet 座標
# ============================================================

def route_to_coordinates(route, weight):

    coordinates = []

    print("Route Node 數量:", len(route))
    print("起點 Node:", route[0])
    print("終點 Node:", route[-1])



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

# ============================================================
# Route API
# ============================================================

@app.route("/api/routes")
def routes():

    case = request.args.get(
        "case",
        "1"
    )


    # ========================================================
    # Case 1
    # 桃園車站 → 台北車站
    # ========================================================

    if case == "1":

        selected_routes = {

            "route1": (
                shortest_distance_route,
                "length"
            ),

            "route2": (
                shortest_time_route,
                "travel_time"
            ),

            "route3": (
                best_compromise_route,
                "compromise_cost"
            )

        }


    # ========================================================
    # Case 2
    # 桃園車站 → 西門町
    # ========================================================

    elif case == "2":

        selected_routes = {

            "route1": (
                case2_route1,
                "length"
            ),

            "route2": (
                case2_route2,
                "travel_time"
            ),

            "route3": (
                case2_route3,
                "compromise_cost"
            )

        }

        
    # ========================================================
    # Case 3
    # 桃園車站 → 信義計畫區
    # ========================================================

    elif case == "3":

        selected_routes = {

            "route1": (
                case3_route1,
                "length"
            ),

            "route2": (
                case3_route2,
                "travel_time"
            ),

            "route3": (
                case3_route3,
                "compromise_cost"
            )

        }






    else:

        return jsonify({
            "error": "Unknown case"
        }), 400


    return jsonify({

        "route1": route_to_coordinates(
            selected_routes["route1"][0],
            selected_routes["route1"][1]
        ),

        "route2": route_to_coordinates(
            selected_routes["route2"][0],
            selected_routes["route2"][1]
        ),

        "route3": route_to_coordinates(
            selected_routes["route3"][0],
            selected_routes["route3"][1]
        )

    })

# ============================================================
# 啟動 Flask
# ============================================================

if __name__ == "__main__":

    app.run(debug=True)


    