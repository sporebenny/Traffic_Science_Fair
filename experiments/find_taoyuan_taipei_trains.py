import json
from datetime import datetime


INPUT_FILE = "data/transit/raw/railway_timetable_raw.json"

TAOYUAN_STATION = "1080"
TAIPEI_STATION = "1000"


def time_to_seconds(time_text):
    time_object = datetime.strptime(time_text, "%H:%M:%S")

    seconds = (
        time_object.hour * 3600
        + time_object.minute * 60
        + time_object.second
    )

    return seconds


def seconds_to_minutes(seconds):
    return seconds / 60


# ==============================
# 讀取時刻表
# ==============================

with open(INPUT_FILE, "r", encoding="utf-8") as file:
    data = json.load(file)


train_infos = data["TrainInfos"]


results = []


# ==============================
# 搜尋桃園 → 臺北
# ==============================

for train in train_infos:

    train_number = train["Train"]
    time_infos = train["TimeInfos"]

    taoyuan_info = None
    taipei_info = None


    for station_info in time_infos:

        station_id = str(station_info["Station"])


        if station_id == TAOYUAN_STATION:
            taoyuan_info = station_info


        if station_id == TAIPEI_STATION:
            taipei_info = station_info


    # 必須兩站都有停
    if taoyuan_info is None:
        continue

    if taipei_info is None:
        continue


    # ==============================
    # 確認桃園 → 臺北方向
    # ==============================

    taoyuan_order = int(taoyuan_info["Order"])
    taipei_order = int(taipei_info["Order"])


    if taoyuan_order >= taipei_order:
        continue


    # ==============================
    # 取得時間
    # ==============================

    departure_time = taoyuan_info["DEPTime"]
    arrival_time = taipei_info["ARRTime"]


    departure_seconds = time_to_seconds(departure_time)
    arrival_seconds = time_to_seconds(arrival_time)


    # 如果跨午夜
    if arrival_seconds < departure_seconds:
        arrival_seconds += 24 * 60 * 60


    ride_seconds = arrival_seconds - departure_seconds
    ride_minutes = seconds_to_minutes(ride_seconds)


    # ==============================
    # 儲存結果
    # ==============================

    result = {
        "train": train_number,
        "taoyuan_departure": departure_time,
        "taipei_arrival": arrival_time,
        "ride_minutes": ride_minutes,
        "taoyuan_order": taoyuan_order,
        "taipei_order": taipei_order
    }


    results.append(result)


# ==============================
# 按照桃園出發時間排序
# ==============================

results.sort(
    key=lambda item: time_to_seconds(item["taoyuan_departure"])
)


# ==============================
# 輸出
# ==============================

print()
print("臺鐵 桃園 → 臺北 實際班次")
print("=" * 75)

print(
    f"{'車次':<8}"
    f"{'桃園出發':<15}"
    f"{'臺北抵達':<15}"
    f"{'預定乘車時間':<15}"
)

print("-" * 75)


for result in results:

    print(
        f"{result['train']:<8}"
        f"{result['taoyuan_departure']:<15}"
        f"{result['taipei_arrival']:<15}"
        f"{result['ride_minutes']:>6.1f} 分鐘"
    )


print("-" * 75)
print("符合條件的班次數量:", len(results))