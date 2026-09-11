


import json
from pathlib import Path


input_path = Path(
    "data/transit/raw/taiwan_railway_stations_raw.json"
)


print("開始讀取臺鐵原始資料...")

with open(input_path, "r", encoding="utf-8") as file:
    data = json.load(file)


print("資料讀取完成！")
print("最外層資料型態:", type(data))


if isinstance(data, list):
    print("資料筆數:", len(data))

    if len(data) > 0:
        print("第一筆資料:")
        print(data[0])


elif isinstance(data, dict):
    print("最外層共有幾個欄位:", len(data))
    print("最外層欄位:")

    for key in data:
        print(" -", key)


else:
    print("目前無法辨識資料格式。")


    