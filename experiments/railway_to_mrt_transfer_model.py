from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments.railway_waiting_time_model import get_next_train

# ============================================================
# 1. 模型參數
# ============================================================

# 官方表列：臺北車站 → 西門站的捷運行車時間
MRT_RIDE_MINUTES = 2

# 轉乘時間候選值（研究情境假設，非實測平均值）
TRANSFER_TIMES = [3, 6, 10]

# 測試用台鐵抵達時間
# 後續整合時，改由台鐵模型傳入，不再固定寫死
TEST_TRA_ARRIVAL_TIME = "08:57:00"


# ============================================================
# 2. 時間轉換
# ============================================================

def convert_time(time_string):
    """將 HH:MM:SS 時間字串轉換成 datetime。"""
    return datetime.strptime(time_string, "%H:%M:%S")


# ============================================================
# 3. 計算轉乘完成時間
# ============================================================

def calculate_mrt_ready_time(
    tra_arrival_time,
    transfer_minutes
):
    """
    輸入：
        tra_arrival_time：台鐵抵達時間，格式 HH:MM:SS
        transfer_minutes：轉乘所需分鐘數

    輸出：
        完成轉乘、可以開始候車的時間
    """

    arrival_time = convert_time(tra_arrival_time)

    ready_time = arrival_time + timedelta(
        minutes=transfer_minutes
    )

    return ready_time


# ============================================================
# 4. 計算抵達西門站時間
# ============================================================

def calculate_ximen_arrival_time(
    mrt_ready_time,
    mrt_wait_minutes=0
):
    """
    輸入：
        mrt_ready_time：可以開始候車的時間
        mrt_wait_minutes：捷運候車分鐘數

    輸出：
        抵達西門站的估計時間

    注意：
        mrt_wait_minutes=0 代表不計候車時間的理想下限，
        不代表實際上不需要等車。
    """

    total_minutes = mrt_wait_minutes + MRT_RIDE_MINUTES

    return mrt_ready_time + timedelta(
        minutes=total_minutes
    )


# ============================================================
# 5. 執行測試
# ============================================================

def main():
    print("=" * 60)
    print("Mission 15：桃園 → 台北 → 西門最小可行模型")
    print("=" * 60)

    # 取得台鐵模型的計算結果
    train = get_next_train("08:00:00")

    if train is None:
        print("找不到可搭乘的台鐵班次。")
        return

    tra_arrival_time = train["arrival"]

    print(f"台鐵車次：{train['train_no']}")
    print(f"桃園出發：{train['departure']}")
    print(f"台北抵達：{tra_arrival_time}")
    print("-" * 60)

    for transfer_minutes in TRANSFER_TIMES:
        mrt_ready_time = calculate_mrt_ready_time(
            tra_arrival_time,
            transfer_minutes
        )

        ximen_arrival_time = calculate_ximen_arrival_time(
            mrt_ready_time
        )

        total_minutes = (
            train["access_minutes"]
            + train["wait_minutes"]
            + train["ride_minutes"]
            + transfer_minutes
            + MRT_RIDE_MINUTES
        )

        print(f"轉乘時間：{transfer_minutes} 分鐘")
        print(
            f"預計抵達西門："
            f"{ximen_arrival_time.strftime('%H:%M:%S')}"
        )
        print(f"全程時間（不計捷運候車）：{total_minutes:.1f} 分鐘")
        print("-" * 60)

    print("模型測試完成。")

if __name__ == "__main__":
    main()
