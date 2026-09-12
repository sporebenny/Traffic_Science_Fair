

import json


INPUT_FILE = "data/transit/raw/railway_timetable_raw.json"


with open(INPUT_FILE, "r", encoding="utf-8") as file:
    data = json.load(file)


train_infos = data["TrainInfos"]


station_ids = set()


for train in train_infos:

    for station_info in train["TimeInfos"]:

        station_id = station_info["Station"]

        station_ids.add(str(station_id))


print("時刻表中的車站代碼數量:", len(station_ids))
print()


print("是否存在桃園 1080:", "1080" in station_ids)
print("是否存在臺北 1000:", "1000" in station_ids)
print()


print("前 50 個車站代碼：")

station_ids_sorted = sorted(station_ids)

for station_id in station_ids_sorted[:50]:
    print(station_id)

    