


from datetime import datetime, timedelta


# ============================================================
# 1. TRA 抵達臺北車站時間
# ============================================================

TRA_ARRIVAL_TIME = "08:39:00"


# ============================================================
# 2. 轉乘成本候選值
# ============================================================

TRANSFER_TIMES = [3, 6, 10]


# ============================================================
# 3. 將時間字串轉換成 datetime
# ============================================================

def convert_time(time_string):
    """
    將 HH:MM:SS 時間字串轉換成 datetime。
    """

    return datetime.strptime(time_string, "%H:%M:%S")


# ============================================================
# 4. 計算 MRT 可開始候車時間
# ============================================================

def calculate_mrt_ready_time(
    tra_arrival_time,
    transfer_minutes
):
    """
    計算：

    MRT ready time
    =
    TRA arrival time
    +
    T_transfer
    """

    arrival_time = convert_time(
        tra_arrival_time
    )

    ready_time = arrival_time + timedelta(
        minutes=transfer_minutes
    )

    return ready_time


# ============================================================
# 5. 執行轉乘模型
# ============================================================

def main():

    print("=" * 60)
    print("TRA → MRT 臺北車站轉乘成本模型")
    print("=" * 60)

    print()
    print(f"TRA 抵達臺北車站：{TRA_ARRIVAL_TIME}")

    print()
    print("開始測試不同 T_transfer")
    print("-" * 60)

    for transfer_minutes in TRANSFER_TIMES:

        mrt_ready_time = calculate_mrt_ready_time(
            TRA_ARRIVAL_TIME,
            transfer_minutes
        )

        print(
            f"T_transfer = "
            f"{transfer_minutes:>2} 分鐘"
        )

        print(
            f"MRT 可開始候車時間："
            f"{mrt_ready_time.strftime('%H:%M:%S')}"
        )

        print()

    print("=" * 60)
    print("TRA → MRT 轉乘模型測試完成")
    print("=" * 60)


# ============================================================
# 6. 程式進入點
# ============================================================

if __name__ == "__main__":
    main()

    

