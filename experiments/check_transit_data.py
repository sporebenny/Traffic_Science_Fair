


import json
from pathlib import Path


input_path = Path(
    "data/transit/raw/taiwan_railway_stations_raw.json"
)


print("開始進行臺鐵車站資料品質檢查...")
print()


with open(input_path, "r", encoding="utf-8") as file:
    stations = json.load(file)


print("總資料筆數:", len(stations))
print()


# ==============================
# 1. 檢查 stationCode
# ==============================

missing_station_code = 0
station_codes = []

for station in stations:

    station_code = station.get("stationCode")

    if station_code is None or station_code == "":
        missing_station_code += 1
    else:
        station_codes.append(station_code)


print("stationCode 缺失數:", missing_station_code)


# ==============================
# 2. 檢查 stationName
# ==============================

missing_station_name = 0

for station in stations:

    station_name = station.get("stationName")

    if station_name is None or station_name == "":
        missing_station_name += 1


print("stationName 缺失數:", missing_station_name)


# ==============================
# 3. 檢查 GPS
# ==============================

missing_gps = 0
invalid_gps = 0

for station in stations:

    gps = station.get("gps")

    if gps is None or gps == "":
        missing_gps += 1

        print(
            "發現 GPS 缺失:",
            station.get("stationCode"),
            station.get("stationName")
        )

        continue

    gps_parts = gps.split()

    if len(gps_parts) != 2:
        invalid_gps += 1
        continue

    try:
        latitude = float(gps_parts[0])
        longitude = float(gps_parts[1])

    except ValueError:
        invalid_gps += 1
        continue


print("GPS 缺失數:", missing_gps)
print("GPS 格式錯誤數:", invalid_gps)


# ==============================
# 4. 檢查 stationCode 重複
# ==============================

duplicate_codes = 0
checked_codes = []

for code in station_codes:

    if code in checked_codes:
        duplicate_codes += 1
    else:
        checked_codes.append(code)


print("stationCode 重複數:", duplicate_codes)


# ==============================
# 5. 總結
# ==============================

print()
print("========== 資料品質檢查結果 ==========")

if (
    missing_station_code == 0
    and missing_station_name == 0
    and missing_gps == 0
    and invalid_gps == 0
    and duplicate_codes == 0
):
    print("結果：PASS")
    print("所有基本欄位皆通過檢查。")

else:
    print("結果：需要進一步檢查")
    print("部分資料存在缺失、格式錯誤或重複。")


