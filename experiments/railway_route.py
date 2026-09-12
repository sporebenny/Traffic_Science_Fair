

import pandas as pd


# ==========================================
# 1. 讀取臺鐵車站資料
# ==========================================

file_path = "data/transit/stations.csv"

print("開始讀取臺鐵車站資料...")

stations = pd.read_csv(file_path)

print("資料讀取完成！")
print("資料筆數:", len(stations))


# ==========================================
# 2. 排除特殊資料
# ==========================================

stations = stations[stations["station_name"] != "臺北-環島"]


# ==========================================
# 3. 找出桃園與臺北
# ==========================================

start_station = "桃園"
end_station = "臺北"


start_index = stations[stations["station_name"] == start_station].index[0]
end_index = stations[stations["station_name"] == end_station].index[0]


# ==========================================
# 4. 建立桃園 → 臺北的研究站序
# ==========================================

if start_index < end_index:
    route_stations = stations.loc[start_index:end_index]
else:
    route_stations = stations.loc[end_index:start_index].iloc[::-1]


# ==========================================
# 5. 輸出研究站序
# ==========================================

print()
print("桃園 → 臺北研究用臺鐵站序")
print("----------------------------------------")

number = 1

for index, station in route_stations.iterrows():
    print(number, station["station_name"])
    number = number + 1

print("----------------------------------------")
print("研究站點數量:", len(route_stations))

