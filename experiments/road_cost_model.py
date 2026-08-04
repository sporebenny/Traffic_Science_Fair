# =====================================
# Road Cost Model v1.0
# Traffic Science Fair
# =====================================


import osmnx as ox
import networkx as nx


print("Road Cost Model 啟動")


# ==============================
# 讀取道路 Graph
# ==============================

G = ox.load_graphml(
    filepath="data/taoyuan.graphml"
)


print("Graph 載入完成")
print(G)



# ==============================
# 取得第一條道路
# ==============================

u, v, key, data = list(G.edges(keys=True, data=True))[0]


print("\n===== 第一條道路 =====")

print("起點 Node：", u)
print("終點 Node：", v)

print("\n道路資料:")
print(data)



# ==============================
# 計算旅行時間
# ==============================

length = data["length"]

speed = float(data["maxspeed"])

speed_ms = speed / 3.6

travel_time = length / speed_ms


print("\n===== Travel Time =====")

print("道路名稱：", data["name"])
print("道路長度：", length, "m")
print("速限：", speed, "km/h")
print("預估時間：", round(travel_time,2), "秒")


