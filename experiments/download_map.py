



import osmnx as ox


print("開始下載桃園-台北道路資料...")


place_name = [
    "Taoyuan District, Taoyuan, Taiwan",
    "Guishan District, Taoyuan, Taiwan",
    "Linkou District, New Taipei, Taiwan",
    "Wugu District, New Taipei, Taiwan",
    "Taipei City, Taiwan"
]


G = ox.graph_from_place(
    place_name,
    network_type="drive"
)


print("下載完成!")

print(G)


print("開始保存 Graph...")


ox.save_graphml(
    G,
    filepath="data/taoyuan_taipei.graphml"
)


print("Graph 保存完成!")