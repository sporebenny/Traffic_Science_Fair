
import csv
from datetime import datetime, timedelta
from pathlib import Path



# ============================================================
# 1. 設定資料檔案位置
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CSV_FILE = (
    PROJECT_ROOT
    / "data"
    / "transit"
    / "railway_trains_taoyuan_taipei.csv"
)


# ============================================================
# 2. 模型參數
# ============================================================

STATION_ACCESS_TIME = 10

SECONDS_PER_DAY = 24 * 60 * 60

REQUIRED_COLUMNS = {
    "train_no",
    "departure",
    "arrival",
    "travel_minutes",
}


# ============================================================
# 3. 時間轉換
# ============================================================

def convert_time(time_string):
    """將 HH:MM:SS 時間字串轉換成 datetime。"""

    try:
        return datetime.strptime(time_string, "%H:%M:%S")
    except (ValueError, TypeError) as error:
        raise ValueError(
            f"無效的時間格式：{time_string!r}，"
            "應使用 HH:MM:SS。"
        ) from error


def time_to_seconds(time_string):
    """將 HH:MM:SS 轉換成當日已經過的秒數。"""

    time_value = convert_time(time_string)

    return (
        time_value.hour * 3600
        + time_value.minute * 60
        + time_value.second
    )


# ============================================================
# 4. 讀取並檢查台鐵班次資料
# ============================================================

def load_train_data():
    """讀取 CSV，檢查必要欄位與資料格式。"""

    if not CSV_FILE.exists():
        raise FileNotFoundError(
            f"找不到台鐵班次資料：{CSV_FILE}"
        )

    trains = []

    with open(
        CSV_FILE,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("台鐵 CSV 沒有欄位標題。")

        missing_columns = REQUIRED_COLUMNS - set(
            reader.fieldnames
        )

        if missing_columns:
            raise ValueError(
                "台鐵 CSV 缺少必要欄位："
                + ", ".join(sorted(missing_columns))
            )

        for row_number, row in enumerate(reader, start=2):

            try:
                train_no = row["train_no"].strip()
                departure = row["departure"].strip()
                arrival = row["arrival"].strip()
                travel_minutes = float(row["travel_minutes"])

                if not train_no:
                    raise ValueError("車次編號不可空白。")

                time_to_seconds(departure)
                time_to_seconds(arrival)

                if (
                    travel_minutes < 0
                    or not 0 <= travel_minutes < 1440
                ):
                    raise ValueError("乘車時間不在合理範圍內。")

                trains.append({
                    "train_no": train_no,
                    "departure": departure,
                    "arrival": arrival,
                    "travel_minutes": travel_minutes,
                })

            except (ValueError, TypeError, AttributeError) as error:
                raise ValueError(
                    f"CSV 第 {row_number} 列資料異常：{error}"
                ) from error

    if not trains:
        raise ValueError("台鐵 CSV 沒有可用的班次資料。")

    return trains


# ============================================================
# 5. 計算使用者真正可以搭車的時間
# ============================================================

def calculate_ready_time(user_arrival_time):
    """
    使用者抵達車站時間 + 進站時間 = 可開始候車時間。
    """

    user_time = convert_time(user_arrival_time)

    return user_time + timedelta(
        minutes=STATION_ACCESS_TIME
    )


# ============================================================
# 6. 計算跨午夜的候車時間
# ============================================================

def calculate_waiting_time(ready_time, train_departure):
    """
    計算下一班車的候車時間。

    使用當日秒數計算時間差；
    若出發時間已跨至隔日凌晨，則將時間差繞回下一日。

    注意：這項計算假設 CSV 班次時刻表可重複套用於隔日。
    """

    ready_seconds = (
        ready_time.hour * 3600
        + ready_time.minute * 60
        + ready_time.second
    )

    departure_seconds = time_to_seconds(train_departure)

    waiting_seconds = (
        departure_seconds - ready_seconds
    ) % SECONDS_PER_DAY

    return waiting_seconds / 60


# ============================================================
# 7. 尋找等待時間最短的下一班車
# ============================================================

def find_next_train(trains, ready_time):
    """
    從所有班次中，找出可在準備完成後搭乘、
    且等待時間最短的班次。

    不依賴 CSV 原本的列車排序。
    """

    if not trains:
        return None

    best_train = None
    shortest_wait = None

    for train in trains:

        wait_minutes = calculate_waiting_time(
            ready_time,
            train["departure"]
        )

        if (
            shortest_wait is None
            or wait_minutes < shortest_wait
        ):
            shortest_wait = wait_minutes
            best_train = train

    return best_train


# ============================================================
# 8. 提供其他模型呼叫的介面
# ============================================================

def get_next_train(user_arrival_time):
    """
    根據使用者抵達桃園車站的時間，
    回傳下一班台鐵及旅程時間資料。

    回傳欄位維持既有格式，
    以相容 railway_to_mrt_transfer_model.py。
    """

    convert_time(user_arrival_time)

    trains = load_train_data()

    ready_time = calculate_ready_time(
        user_arrival_time
    )

    next_train = find_next_train(
        trains,
        ready_time
    )

    if next_train is None:
        return None

    wait_minutes = calculate_waiting_time(
        ready_time,
        next_train["departure"]
    )

    return {
        "train_no": next_train["train_no"],
        "departure": next_train["departure"],
        "arrival": next_train["arrival"],
        "access_minutes": STATION_ACCESS_TIME,
        "wait_minutes": wait_minutes,
        "ride_minutes": next_train["travel_minutes"],
    }


# ============================================================
# 9. 執行等待時間模型
# ============================================================

def main():

    print("=" * 60)
    print("TRA 桃園 → 臺北等待時間模型")
    print("=" * 60)

    user_arrival_time = "08:00:00"

    print(f"班次資料：{CSV_FILE}")
    print(f"使用者抵達桃園車站：{user_arrival_time}")
    print(f"進站時間：{STATION_ACCESS_TIME} 分鐘")

    try:
        trains = load_train_data()

        ready_time = calculate_ready_time(
            user_arrival_time
        )

        next_train = find_next_train(
            trains,
            ready_time
        )

    except (OSError, ValueError) as error:
        print(f"模型執行失敗：{error}")
        return

    print(f"載入班次數量：{len(trains)}")
    print(f"可開始候車時間：{ready_time.strftime('%H:%M:%S')}")

    if next_train is None:
        print("沒有可用的台鐵班次。")
        return

    wait_minutes = calculate_waiting_time(
        ready_time,
        next_train["departure"]
    )

    ride_minutes = next_train["travel_minutes"]

    total_railway_minutes = (
        STATION_ACCESS_TIME
        + wait_minutes
        + ride_minutes
    )

    print("-" * 60)
    print(f"車次：{next_train['train_no']}")
    print(f"桃園出發：{next_train['departure']}")
    print(f"臺北抵達：{next_train['arrival']}")
    print(f"T_access：{STATION_ACCESS_TIME:.1f} 分鐘")
    print(f"T_wait：{wait_minutes:.1f} 分鐘")
    print(f"T_ride：{ride_minutes:.1f} 分鐘")
    print(f"T_railway：{total_railway_minutes:.1f} 分鐘")
    print("=" * 60)
    print("等待時間模型執行完成")


if __name__ == "__main__":
    main()


