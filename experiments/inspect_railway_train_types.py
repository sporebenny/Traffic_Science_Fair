

import json


# ==========================================
# 1. 讀取原始時刻表
# ==========================================

file_path = "data/transit/raw/railway_timetable_raw.json"

with open(file_path, "r", encoding="utf-8") as file:

    data = json.load(file)


# ==========================================
# 2. 取得 TrainInfos
# ==========================================

train_infos = data["TrainInfos"]


print("臺鐵時刻表車次類型統計")
print("----------------------------------------")

print("總車次數量:", len(train_infos))


# ==========================================
# 3. 統計 Type
# ==========================================

type_counts = {}


for train in train_infos:

    train_type = train.get("Type", "")

    if train_type not in type_counts:

        type_counts[train_type] = 0

    type_counts[train_type] += 1


# ==========================================
# 4. 印出結果
# ==========================================

print("----------------------------------------")
print("Type 統計")
print("----------------------------------------")

for train_type, count in type_counts.items():

    print(
        "Type:",
        train_type,
        "車次數:",
        count
    )



    print("----------------------------------------")
print("各 Type 範例車次")
print("----------------------------------------")

example_types = {}

for train in train_infos:

    train_type = train.get("Type", "")

    if train_type not in example_types:

        example_types[train_type] = train


for train_type, train in example_types.items():

    print()
    print("Type:", train_type)
    print("Train:", train.get("Train"))
    print("Everyday:", train.get("Everyday"))
    print("Line:", train.get("Line"))
    print("LineDir:", train.get("LineDir"))
    print("CarClass:", train.get("CarClass"))
    print("Note:", train.get("Note"))



print("----------------------------------------")
print("CarClass 統計")
print("----------------------------------------")

car_class_counts = {}

for train in train_infos:

    car_class = train.get("CarClass", "")

    if car_class not in car_class_counts:

        car_class_counts[car_class] = 0

    car_class_counts[car_class] += 1


for car_class, count in car_class_counts.items():

    print(
        "CarClass:",
        car_class,
        "車次數:",
        count
    )

    