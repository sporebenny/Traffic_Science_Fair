

import json
from pathlib import Path


input_path = Path(
    "data/transit/raw/taiwan_railway_stations_raw.json"
)


with open(input_path, "r", encoding="utf-8") as file:
    stations = json.load(file)


target_names = [
    "中壢",
    "桃園",
    "臺北",
    "南港"
]


print("開始搜尋研究範圍車站...")
print()


for target_name in target_names:

    found = False

    for station in stations:

        station_name = station.get("stationName")

        if station_name == target_name:

            print("找到車站:")
            print("  車站名稱:", station_name)
            print("  stationCode:", station.get("stationCode"))
            print("  GPS:", station.get("gps"))
            print()

            found = True

    if found == False:

        print("找不到車站:", target_name)
        print()

        