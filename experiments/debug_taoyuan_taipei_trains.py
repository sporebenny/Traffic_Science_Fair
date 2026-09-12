
import json


INPUT_FILE = "data/transit/raw/railway_timetable_raw.json"

TAOYUAN_STATION = "1080"
TAIPEI_STATION = "1000"


with open(INPUT_FILE, "r", encoding="utf-8") as file:
    data = json.load(file)


train_infos = data["TrainInfos"]


taoyuan_count = 0
taipei_count = 0
both_count = 0
correct_order_count = 0


print("開始檢查桃園 → 臺北班次")
print("=" * 70)


for train in train_infos:

    time_infos = train["TimeInfos"]

    taoyuan_info = None
    taipei_info = None


    for station_info in time_infos:

        station_id = str(station_info["Station"])


        if station_id == TAOYUAN_STATION:
            taoyuan_info = station_info


        if station_id == TAIPEI_STATION:
            taipei_info = station_info


    # 有停桃園
    if taoyuan_info is not None:
        taoyuan_count += 1


    # 有停臺北
    if taipei_info is not None:
        taipei_count += 1


    # 兩站都有停
    if taoyuan_info is not None and taipei_info is not None:

        both_count += 1


        taoyuan_order = int(taoyuan_info["Order"])
        taipei_order = int(taipei_info["Order"])


        # 桃園 → 臺北
        if taoyuan_order < taipei_order:

            correct_order_count += 1


            if correct_order_count <= 10:

                print(
                    "車次:",
                    train["Train"],
                    "| 桃園 Order:",
                    taoyuan_order,
                    "| 臺北 Order:",
                    taipei_order
                )


print()
print("=" * 70)
print("診斷結果")
print("=" * 70)

print("總車次:", len(train_infos))
print("停靠桃園:", taoyuan_count)
print("停靠臺北:", taipei_count)
print("兩站都有停:", both_count)
print("桃園 → 臺北:", correct_order_count)

