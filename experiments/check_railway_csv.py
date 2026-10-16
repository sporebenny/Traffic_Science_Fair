import csv
from datetime import datetime
from collections import Counter
from pathlib import Path

CSV_FILE = Path("data/transit/railway_trains_taoyuan_taipei.csv")
REQUIRED_FIELDS = ["train_no", "departure", "arrival", "travel_minutes"]


def main():
    with CSV_FILE.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        fields = reader.fieldnames

    print("=== 台鐵 CSV 資料品質檢查 ===")
    print("欄位名稱：", fields)
    print("班次總數：", len(rows))

    # 1. 檢查必要欄位
    missing_fields = [
        field for field in REQUIRED_FIELDS
        if field not in (fields or [])
    ]

    if missing_fields:
        print("缺少必要欄位：", missing_fields)
        return

    # 2. 檢查出發時間排序
    invalid_times = []
    departures = []

    for index, row in enumerate(rows, start=2):
        try:
            departure = datetime.strptime(
                row["departure"], "%H:%M:%S"
            )
            departures.append(departure)
        except (ValueError, TypeError):
            invalid_times.append((index, row.get("departure")))

    order_errors = []

    for index in range(len(departures) - 1):
        if departures[index] > departures[index + 1]:
            order_errors.append(index + 2)

    print("出發時間排序異常：", len(order_errors))
    if order_errors:
        print("異常位置（CSV 列號）：", order_errors[:10])

    print("無法解析的出發時間：", len(invalid_times))
    if invalid_times:
        print("異常資料：", invalid_times[:10])

    # 3. 檢查重複車次編號
    train_counts = Counter(row["train_no"] for row in rows)
    duplicates = [
        train_no for train_no, count in train_counts.items()
        if count > 1
    ]

    print("重複車次編號種類：", len(duplicates))
    if duplicates:
        print("重複編號範例：", duplicates[:10])

    # 4. 檢查必要欄位缺漏
    missing_rows = [
        (index, row)
        for index, row in enumerate(rows, start=2)
        if any(not row.get(field, "").strip()
               for field in REQUIRED_FIELDS)
    ]

    print("必要欄位缺漏筆數：", len(missing_rows))
    if missing_rows:
        print("缺漏資料範例：", missing_rows[:3])

    # 5. 比較乘車時間與出發、抵達時間差
    mismatches = []
    invalid_duration_rows = []

    for index, row in enumerate(rows, start=2):
        try:
            departure = datetime.strptime(
                row["departure"], "%H:%M:%S"
            )
            arrival = datetime.strptime(
                row["arrival"], "%H:%M:%S"
            )

            actual_minutes = (
                arrival - departure
            ).total_seconds() / 60

            # 若抵達時間早於出發時間，先視為跨日候選資料
            if actual_minutes < 0:
                actual_minutes += 24 * 60

            recorded_minutes = float(row["travel_minutes"])

            if abs(actual_minutes - recorded_minutes) > 0.01:
                mismatches.append({
                    "row": index,
                    "train_no": row["train_no"],
                    "departure": row["departure"],
                    "arrival": row["arrival"],
                    "recorded_minutes": recorded_minutes,
                    "calculated_minutes": actual_minutes,
                })

        except (ValueError, TypeError):
            invalid_duration_rows.append(index)

    print("乘車時間不一致筆數：", len(mismatches))
    if mismatches:
        print("不一致資料範例：", mismatches[:10])

    print("無法計算乘車時間的列數：", len(invalid_duration_rows))
    if invalid_duration_rows:
        print("異常列號：", invalid_duration_rows[:10])

    print("=== 檢查完成（尚未驗證官方來源與營運日期） ===")


if __name__ == "__main__":
    main()