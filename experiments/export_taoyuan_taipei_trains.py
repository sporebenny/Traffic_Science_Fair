

import json
import csv
from pathlib import Path
from datetime import datetime


# ============================================================
# 1. 資料位置
# ============================================================

input_path = Path(
    "data/transit/raw/railway_timetable_raw.json"
)

output_path = Path(
    "data/transit/railway_trains_taoyuan_taipei.csv"
)


# ============================================================
# 2. 研究車站代碼
# ============================================================

TAOYUAN_STATION = "1080"
TAIPEI_STATION = "1000"


# ============================================================
# 3. 讀取臺鐵原始時刻表
# ============================================================

print("開始讀取臺鐵原始時刻表...")
print("----------------------------------------")

with open(input_path, "r", encoding="utf-8") as file:
    data = json.load(file)

train_infos = data["TrainInfos"]

print("原始車次數量:", len(train_infos))


# ============================================================
# 4. 篩選桃園 → 臺北班次
# ============================================================

qualified_trains = []

for train in train_infos:

    time_infos = train.get("TimeInfos", [])

    taoyuan_info = None
    taipei_info = None

    for station in time_infos:

        station_code = station.get("Station")

        if station_code == TAOYUAN_STATION:
            taoyuan_info = station

        elif station_code == TAIPEI_STATION:
            taipei_info = station

    # 必須兩站都有停靠
    if taoyuan_info is None or taipei_info is None:
        continue

    # 確認順序：桃園必須在臺北之前
    taoyuan_order = int(taoyuan_info["Order"])
    taipei_order = int(taipei_info["Order"])

    if taoyuan_order >= taipei_order:
        continue

    departure = taoyuan_info["DEPTime"]
    arrival = taipei_info["ARRTime"]

    # --------------------------------------------------------
    # 計算預定乘車時間
    # --------------------------------------------------------

    departure_time = datetime.strptime(
        departure,
        "%H:%M:%S"
    )

    arrival_time = datetime.strptime(
        arrival,
        "%H:%M:%S"
    )

    # 跨午夜處理
    if arrival_time < departure_time:
        arrival_time = arrival_time.replace(
            day=arrival_time.day + 1
        )

    travel_seconds = (
        arrival_time - departure_time
    ).total_seconds()

    travel_minutes = travel_seconds / 60

    qualified_trains.append(
        {
            "train_no": train["Train"],
            "departure": departure,
            "arrival": arrival,
            "travel_minutes": travel_minutes
        }
    )


# ============================================================
# 5. 按桃園出發時間排序
# ============================================================

qualified_trains.sort(
    key=lambda train: train["departure"]
)


# ============================================================
# 6. 建立輸出資料夾
# ============================================================

output_path.parent.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 7. 輸出 CSV
# ============================================================

with open(
    output_path,
    "w",
    newline="",
    encoding="utf-8-sig"
) as file:

    writer = csv.writer(file)

    writer.writerow(
        [
            "train_no",
            "departure",
            "arrival",
            "travel_minutes"
        ]
    )

    for train in qualified_trains:

        writer.writerow(
            [
                train["train_no"],
                train["departure"],
                train["arrival"],
                f"{train['travel_minutes']:.1f}"
            ]
        )


# ============================================================
# 8. 顯示結果
# ============================================================

print("----------------------------------------")
print("臺鐵桃園 → 臺北研究班次")
print("----------------------------------------")

print(
    "符合條件的班次數量:",
    len(qualified_trains)
)

print(
    "CSV 已建立:",
    output_path
)

print("----------------------------------------")
print("前 5 筆資料")
print("----------------------------------------")

for train in qualified_trains[:5]:

    print(
        train["train_no"],
        train["departure"],
        train["arrival"],
        f"{train['travel_minutes']:.1f} 分鐘"
    )


    