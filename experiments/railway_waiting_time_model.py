import csv
from datetime import datetime, timedelta


# ============================================================
# 1. 設定資料檔案位置
# ============================================================

CSV_FILE = "data/transit/railway_trains_taoyuan_taipei.csv"


# ============================================================
# 2. 車站進站與前往月台所需時間
# ============================================================

STATION_ACCESS_TIME = 10


# ============================================================
# 3. 將 HH:MM:SS 轉換成 datetime
# ============================================================

def convert_time(time_string):
    """
    將時間字串轉換成 datetime。
    """

    return datetime.strptime(time_string, "%H:%M:%S")


# ============================================================
# 4. 讀取台鐵桃園 → 臺北班次
# ============================================================

def load_train_data():
    """
    讀取桃園 → 臺北的台鐵班次資料。
    """

    trains = []

    with open(CSV_FILE, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            trains.append(row)

    return trains


# ============================================================
# 5. 計算使用者真正可以搭車的時間
# ============================================================

def calculate_ready_time(user_arrival_time):
    """
    使用者到站後，
    加上車站進站與前往月台時間。

    user_arrival_time
        +
    T_access
        =
    user_ready_time
    """

    user_time = convert_time(user_arrival_time)

    ready_time = user_time + timedelta(
        minutes=STATION_ACCESS_TIME
    )

    return ready_time


# ============================================================
# 6. 找出使用者真正可以搭乘的下一班車
# ============================================================

def find_next_train(trains, ready_time):
    """
    根據使用者真正準備完成的時間，
    找出第一班可以搭乘的列車。
    """

    for train in trains:

        departure_time = convert_time(train["departure"])

        if departure_time >= ready_time:
            return train

    return None


# ============================================================
# 7. 計算等待時間 T_wait
# ============================================================

def calculate_waiting_time(ready_time, train_departure):
    """
    計算：

    T_wait = 下一班車出發時間 - user_ready_time
    """

    departure_time = convert_time(train_departure)

    waiting_time = departure_time - ready_time

    waiting_minutes = waiting_time.total_seconds() / 60

    return waiting_minutes


# ============================================================
# 8. 執行等待時間模型
# ============================================================

def main():

    print("=" * 60)
    print("TRA 桃園 → 臺北等待時間模型")
    print("=" * 60)

    # --------------------------------------------------------
    # 讀取班次資料
    # --------------------------------------------------------

    trains = load_train_data()

    print()
    print(f"載入班次數量：{len(trains)}")

    # --------------------------------------------------------
    # 設定測試情境
    # --------------------------------------------------------

    user_arrival_time = "08:00:00"

    print()
    print(f"使用者到達桃園車站時間：{user_arrival_time}")
    print(f"T_access：{STATION_ACCESS_TIME} 分鐘")

    # --------------------------------------------------------
    # 計算真正準備完成時間
    # --------------------------------------------------------

    ready_time = calculate_ready_time(
        user_arrival_time
    )

    print(f"可開始候車時間：{ready_time.strftime('%H:%M:%S')}")
    print()

    # --------------------------------------------------------
    # 找下一班車
    # --------------------------------------------------------

    next_train = find_next_train(
        trains,
        ready_time
    )

    # --------------------------------------------------------
    # 判斷是否找到班次
    # --------------------------------------------------------

    if next_train is None:

        print("找不到可搭乘的下一班車。")
        print("可能原因：當天已沒有後續班次。")

        return

    # --------------------------------------------------------
    # 取出下一班列車資料
    # --------------------------------------------------------

    train_no = next_train["train_no"]
    departure = next_train["departure"]
    arrival = next_train["arrival"]
    ride_minutes = float(next_train["travel_minutes"])

    # --------------------------------------------------------
    # 計算等待時間
    # --------------------------------------------------------

    wait_minutes = calculate_waiting_time(
        ready_time,
        departure
    )

    # --------------------------------------------------------
    # 計算台鐵總時間
    # --------------------------------------------------------

    total_railway_minutes = (
        STATION_ACCESS_TIME
        + wait_minutes
        + ride_minutes
    )

    # --------------------------------------------------------
    # 顯示結果
    # --------------------------------------------------------

    print("找到下一班可搭乘列車")
    print("-" * 60)

    print(f"車次：{train_no}")
    print(f"桃園出發：{departure}")
    print(f"臺北抵達：{arrival}")

    print()
    print(f"T_access：{STATION_ACCESS_TIME:.1f} 分鐘")
    print(f"T_wait：{wait_minutes:.1f} 分鐘")
    print(f"T_ride：{ride_minutes:.1f} 分鐘")

    print()
    print(f"T_railway：{total_railway_minutes:.1f} 分鐘")

    print()
    print("=" * 60)
    print("等待時間模型執行完成")
    print("=" * 60)


# ============================================================
# 9. 程式進入點
# ============================================================

if __name__ == "__main__":
    main()


