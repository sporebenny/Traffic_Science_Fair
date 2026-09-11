

import json
from pathlib import Path


# 官方臺鐵原始資料的位置
input_path = Path("data/transit/raw/taiwan_railway_stations_raw.json")


print("開始讀取臺鐵原始資料...")

with open(input_path, "r", encoding="utf-8") as file:
    stations = json.load(file)


print("資料讀取完成！")
print("原始資料筆數:", len(stations))
print()


# 研究範圍的車站代碼
start_code = 980
end_code = 1100


selected_stations = []


for station in stations:

    station_code = station.get("stationCode")

    if station_code is None:
        continue

    station_code_number = int(station_code)

    if start_code <= station_code_number <= end_code:

        selected_stations.append(station)


# 按 stationCode 排序
selected_stations.sort(
    key=lambda station: int(station["stationCode"])
)


print("研究範圍內的臺鐵車站：")
print("----------------------------------------")


for station in selected_stations:

    print(
        station["stationCode"],
        station["stationName"],
        station["gps"]
    )


print("----------------------------------------")
print("候選車站數量:", len(selected_stations))

