
import argparse
import csv
from pathlib import Path
from datetime import datetime, time


# ==========================================
# 1. 資料路徑
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

TIMETABLE_PATH = (
    PROJECT_ROOT
    / "data"
    / "transit"
    / "railway_trains_taoyuan_taipei.csv"
)


# ==========================================
# 2. 時間處理
# ==========================================

def parse_time(value):
    """將多種時間格式轉換成 time。"""

    value = str(value).strip()

    formats = (
        "%H:%M:%S",
        "%H:%M",
        "%H%M",
    )

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).time()
        except ValueError:
            continue

    raise ValueError(f"無法辨識時間格式：{value}")


# ==========================================
# 3. 讀取臺鐵時刻表
# ==========================================

def load_timetable(file_path=TIMETABLE_PATH):
    """讀取桃園至臺北的臺鐵時刻表 CSV。"""

    trains = []

    with open(file_path, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        required_columns = {
            "train_no",
            "departure",
            "arrival",
            "travel_minutes",
        }

        if not required_columns.issubset(reader.fieldnames or []):
            raise ValueError(
                "CSV 欄位不完整，必要欄位為："
                "train_no、departure、arrival、travel_minutes"
            )

        for row in reader:
            trains.append(row)

    return trains


# ==========================================
# 4. 尋找下一班列車
# ==========================================

def select_next_train(trains, passenger_arrival_time):
    """
    根據旅客抵達桃園車站的時間，
    找出當日時刻表中下一班桃園至臺北列車。
    """

    passenger_time = parse_time(passenger_arrival_time)

    candidates = []

    for train in trains:
        departure_time = parse_time(train["departure"])

        # 只考慮旅客抵達車站之後出發的列車
        if departure_time < passenger_time:
            continue

        waiting_minutes = (
            datetime.combine(datetime.today(), departure_time)
            - datetime.combine(datetime.today(), passenger_time)
        ).total_seconds() / 60

        candidates.append({
            "train_no": train["train_no"],
            "departure": departure_time.strftime("%H:%M"),
            "arrival": parse_time(train["arrival"]).strftime("%H:%M"),
            "waiting_minutes": int(waiting_minutes),
            "travel_minutes": float(train["travel_minutes"]),
        })

    if not candidates:
        return None

    candidates.sort(key=lambda item: item["waiting_minutes"])

    return candidates[0]


# ==========================================
# 5. 顯示選擇結果
# ==========================================

def display_result(result, research_date):
    print("\n========== PT-06A 臺鐵下一班列車選擇器 ==========")
    print(f"研究日期：{research_date}")

    if result is None:
        print("找不到旅客抵達時間之後的列車。")
        print("請確認抵達時間或時刻表資料。")
        return

    total_minutes = (
        result["waiting_minutes"] + result["travel_minutes"]
    )

    print(f"選擇車次：{result['train_no']}")
    print(f"桃園站發車時間：{result['departure']}")
    print(f"臺北站抵達時間：{result['arrival']}")
    print(f"候車時間：{result['waiting_minutes']:.0f} 分鐘")
    print(f"臺鐵乘車時間：{result['travel_minutes']:.0f} 分鐘")
    print(f"候車＋乘車時間：{total_minutes:.0f} 分鐘")

    print("\n資料限制：")
    print("班次適用日期尚待驗證，以上結果為時刻表選擇結果。")
    print("================================================")


# ==========================================
# 6. 程式入口
# ==========================================

def main():
    parser = argparse.ArgumentParser(
        description="臺鐵下一班列車自動選擇器"
    )

    parser.add_argument(
        "--arrival",
        required=True,
        help="旅客抵達桃園車站時間，例如 07:30",
    )

    parser.add_argument(
        "--date",
        default="2026-09-12",
        help="研究日期，預設為 2026-09-12",
    )

    args = parser.parse_args()

    trains = load_timetable()

    result = select_next_train(
        trains,
        args.arrival,
    )

    display_result(result, args.date)


if __name__ == "__main__":
    main()


    