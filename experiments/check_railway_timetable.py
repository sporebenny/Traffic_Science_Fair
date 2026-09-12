

import json


# ==========================================
# 1. 原始臺鐵時刻資料
# ==========================================

file_path = "data/transit/raw/railway_timetable_raw.json"


# ==========================================
# 2. 讀取 JSON
# ==========================================

with open(file_path, "r", encoding="utf-8") as file:

    data = json.load(file)


# ==========================================
# 3. 顯示基本資料結構
# ==========================================

print("資料讀取成功！")
print("----------------------------------------")

print("資料型態:", type(data))

if isinstance(data, list):

    print("資料筆數:", len(data))

elif isinstance(data, dict):

    print("最外層欄位:")

    for key in data.keys():

        print("-", key)


# ==========================================
# 4. 印出資料內容
# ==========================================

print("----------------------------------------")
print("資料內容")
print("----------------------------------------")

if isinstance(data, list):

    for i in range(min(3, len(data))):

        print()
        print("第", i + 1, "筆:")

        print(
            json.dumps(
                data[i],
                ensure_ascii=False,
                indent=2
            )
        )


elif isinstance(data, dict):

    print(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        )[:8000]
    )


# ==========================================
# 5. 檢查第一筆資料欄位
# ==========================================

print("----------------------------------------")
print("第一筆資料的欄位")
print("----------------------------------------")

if isinstance(data, list) and len(data) > 0:

    first_item = data[0]

    if isinstance(first_item, dict):

        for key in first_item.keys():

            print("-", key)

