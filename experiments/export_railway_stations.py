

import json
import pandas as pd
from pathlib import Path


# ==========================================
# 1. 設定檔案
# ==========================================

input_path = Path(
    "data/transit/raw/taiwan_railway_stations_raw.json"
)

output_path = Path(
    "data/transit/stations.csv"
)


# ==========================================
# 2. 讀取原始 JSON
# ==========================================

print("開始讀取臺鐵原始資料...")

with open(input_path, "r", encoding="utf-8") as file:
    stations = json.load(file)

print("原始資料筆數:", len(stations))


# ==========================================
# 3. 篩選研究範圍
# ==========================================

research_stations = []

for station in stations:

    station_code = station.get("stationCode")
    station_name = station.get("stationName")
    gps = station.get("gps")

    if station_code is None:
        continue

    try:
        code_number = int(station_code)
    except ValueError:
        continue

    # 南港 0980 ～ 中壢 1100
    if code_number < 980 or code_number > 1100:
        continue

    # 排除特殊資料「臺北-環島」
    if station_name == "臺北-環島":
        continue

    if gps is None or gps == "":
        continue

    gps_parts = gps.split()

    if len(gps_parts) != 2:
        continue

    try:
        latitude = float(gps_parts[0])
        longitude = float(gps_parts[1])
    except ValueError:
        continue

    research_stations.append(
        {
            "station_id": station_code,
            "station_name": station_name,
            "transport_type": "TRA",
            "latitude": latitude,
            "longitude": longitude
        }
    )


# ==========================================
# 4. 按照車站代碼排序
# ==========================================

research_stations.sort(
    key=lambda station: int(station["station_id"])
)


# ==========================================
# 5. 建立 DataFrame
# ==========================================

data = pd.DataFrame(research_stations)


# ==========================================
# 6. 輸出 CSV
# ==========================================

output_path.parent.mkdir(
    parents=True,
    exist_ok=True
)

data.to_csv(
    output_path,
    index=False,
    encoding="utf-8-sig"
)


# ==========================================
# 7. 顯示結果
# ==========================================

print()
print("研究範圍內的臺鐵車站")
print("----------------------------------------")

number = 1

for station in research_stations:

    print(
        number,
        station["station_id"],
        station["station_name"],
        station["latitude"],
        station["longitude"]
    )

    number = number + 1


print("----------------------------------------")
print("研究用車站數量:", len(research_stations))
print("CSV 已建立:", output_path)

