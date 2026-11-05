
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from experiments.railway_waiting_time_model import get_next_train
from experiments.mrt_travel_time_model import get_mrt_travel_time
from dataclasses import dataclass, asdict
from typing import Any

# ============================================================
# 1. 模型參數
# ============================================================

# 臺北車站 → 西門站的捷運路段設定
MRT_ORIGIN_CODE = "BL12"
MRT_DESTINATION_CODE = "BL11"
MRT_LINE = "BL"
MRT_DIRECTION = "往頂埔"

# 轉乘時間情境（研究假設，非實測平均值）
TRANSFER_TIMES = [3, 6, 10]

# 捷運候車時間情境（研究假設，非實測平均值）
MRT_WAIT_TIMES = [0, 3, 5]

# 使用者抵達桃園車站的測試時間
USER_ARRIVAL_TIMES = [
    "07:30:00",
    "08:00:00",
    "08:30:00",
]


# ============================================================
# 統一旅程結果資料結構
# ============================================================

@dataclass
class JourneyResult:
    """統一不同運具的旅程結果格式。"""

    # 情境識別
    scenario_id: str

    # 運具與旅程基本資訊
    mode: str
    origin: str
    destination: str

    # 時間資訊
    user_start_time: str
    first_vehicle_departure_time: str
    arrival_time: str
    total_minutes: float

    # 各階段耗時與相關時間
    stages: list[dict[str, Any]]

    # 重要時間節點
    milestones: dict[str, str]

    # 資料來源、研究假設與估算限制
    assumptions: list[str]


# ============================================================
# 2. 時間轉換與輸入檢查
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
    """計算台鐵抵達後，完成轉乘並可開始候車的時間。"""

    arrival_time = convert_time(tra_arrival_time)

    return arrival_time + timedelta(
        minutes=transfer_minutes
    )


# ============================================================
# 4. 計算抵達西門站時間
# ============================================================

def calculate_ximen_arrival_time(
    mrt_ready_time,
    mrt_wait_minutes,
    mrt_ride_minutes
):
    """計算包含捷運候車與行車時間的預計抵達時間。"""

    total_mrt_minutes = (
        mrt_wait_minutes + mrt_ride_minutes
    )

    return mrt_ready_time + timedelta(
        minutes=total_mrt_minutes
    )

# ============================================================
# 5. 計算全程旅行時間
# ============================================================

def calculate_total_minutes(
    train,
    transfer_minutes,
    mrt_wait_minutes,
    mrt_ride_minutes
):
    """計算桃園車站至西門站的全程模型時間。"""

    return (
        train["access_minutes"]
        + train["wait_minutes"]
        + train["ride_minutes"]
        + transfer_minutes
        + mrt_wait_minutes
        + mrt_ride_minutes
    )

# ============================================================
# 6. 計算單一出發時間的所有情境
# ============================================================


def calculate_journey_scenarios(user_arrival_time):
    """
    根據使用者抵達桃園車站的時間，
    計算臺鐵與所有轉乘、捷運候車情境。

    回傳：
        train：臺鐵模型結果
        scenarios：完整旅程情境列表
    """

    # 驗證使用者輸入的時間格式
    convert_time(user_arrival_time)

    # 呼叫既有臺鐵模型
    train = get_next_train(user_arrival_time)

    if train is None:
        return None, []

    # 從捷運資料表取得臺北車站至西門站的乘車時間
    mrt_ride_minutes = get_mrt_travel_time(
        origin_code=MRT_ORIGIN_CODE,
        destination_code=MRT_DESTINATION_CODE,
        line=MRT_LINE,
        direction=MRT_DIRECTION,
    )

    # 臺鐵階段總時間
    tra_total_minutes = (
        train["access_minutes"]
        + train["wait_minutes"]
        + train["ride_minutes"]
    )

    scenarios = []

    for transfer_minutes in TRANSFER_TIMES:
        mrt_ready_time = calculate_mrt_ready_time(
            train["arrival"],
            transfer_minutes
        )

        for mrt_wait_minutes in MRT_WAIT_TIMES:
            ximen_arrival_time = calculate_ximen_arrival_time(
                mrt_ready_time,
                mrt_wait_minutes,
                mrt_ride_minutes,
            )

            total_minutes = calculate_total_minutes(
                train,
                transfer_minutes,
                mrt_wait_minutes,
                mrt_ride_minutes,
            )

            scenarios.append({
                # 使用者輸入
                "user_arrival_time": user_arrival_time,

                # 臺鐵階段
                "train_no": train["train_no"],
                "tra_departure": train["departure"],
                "tra_arrival": train["arrival"],
                "access_minutes": train["access_minutes"],
                "tra_wait_minutes": train["wait_minutes"],
                "tra_ride_minutes": train["ride_minutes"],
                "tra_total_minutes": tra_total_minutes,

                # 轉乘與捷運階段
                "transfer_minutes": transfer_minutes,
                "mrt_wait_minutes": mrt_wait_minutes,
                "mrt_ride_minutes": mrt_ride_minutes,

                # 全程結果
                "ximen_arrival_time": (
                    ximen_arrival_time.strftime("%H:%M:%S")
                ),
                "total_minutes": total_minutes,
            })

    return train, scenarios



def build_journey_result(user_arrival_time, scenario, scenario_id):
    """將單一大眾運輸情境轉換成統一的 JourneyResult。"""

    stages = [
        {
            "stage_id": "access",
            "name": "車站進站",
            "mode": "walking",
            "minutes": scenario["access_minutes"],
        },
        {
            "stage_id": "tra_wait",
            "name": "臺鐵候車",
            "mode": "waiting",
            "minutes": scenario["tra_wait_minutes"],
        },
        {
            "stage_id": "tra_ride",
            "name": "臺鐵乘車",
            "mode": "railway",
            "minutes": scenario["tra_ride_minutes"],
        },
        {
            "stage_id": "transfer",
            "name": "轉乘",
            "mode": "transfer",
            "minutes": scenario["transfer_minutes"],
        },
        {
            "stage_id": "mrt_wait",
            "name": "捷運候車",
            "mode": "waiting",
            "minutes": scenario["mrt_wait_minutes"],
        },
        {
            "stage_id": "mrt_ride",
            "name": "捷運乘車",
            "mode": "metro",
            "minutes": scenario["mrt_ride_minutes"],
        },
    ]

    assumptions = [
        "旅行時間為模型估算，不是即時交通預報。",
        "車站進站時間採用既有模型設定。",
        "轉乘時間為研究假設。",
        "捷運候車時間為研究情境假設。",
        "捷運乘車時間採用目前模型參數。",
    ]

    return JourneyResult(
        scenario_id=scenario_id,
        mode="public_transport",
        origin="桃園車站",
        destination="西門站",
        user_start_time=user_arrival_time,
        first_vehicle_departure_time=scenario["tra_departure"],
        arrival_time=scenario["ximen_arrival_time"],
        total_minutes=scenario["total_minutes"],
        stages=stages,
        milestones={
            "tra_departure": scenario["tra_departure"],
            "tra_arrival": scenario["tra_arrival"],
        },
        assumptions=assumptions,
    )





def calculate_journey_results(user_arrival_time):
    """產生具有獨立情境編號的統一旅程結果。"""

    train, scenarios = calculate_journey_scenarios(
        user_arrival_time
    )

    if train is None:
        return []

    results = []

    for index, scenario in enumerate(scenarios, start=1):
        result = build_journey_result(
            user_arrival_time,
            scenario,
            scenario_id=f"PT-{index:02d}",
        )
        results.append(result)

    return results




def get_journey_results_as_dict(user_arrival_time):
    """
    取得適合 Flask API 使用的旅程結果字典列表。
    """

    results = calculate_journey_results(user_arrival_time)

    return [
        asdict(result)
        for result in results
    ]


def print_journey_result(user_arrival_time):
    """顯示指定出發時間的台鐵資料與旅程情境。"""

    print()
    print("=" * 68)
    print(f"使用者抵達桃園車站：{user_arrival_time}")
    print("=" * 68)

    try:
        train, scenarios = calculate_journey_scenarios(
            user_arrival_time
        )
    except ValueError:
        print("時間格式錯誤，請使用 HH:MM:SS，例如 08:00:00。")
        return

    if train is None:
        print("找不到可搭乘的下一班台鐵列車。")
        print("請確認班次資料及目前模型支援的時間範圍。")
        return

    railway_total = (
        train["access_minutes"]
        + train["wait_minutes"]
        + train["ride_minutes"]
    )

    print(f"台鐵車次：{train['train_no']}")
    print(f"桃園出發：{train['departure']}")
    print(f"臺北抵達：{train['arrival']}")
    print(f"進站時間：{train['access_minutes']:.1f} 分鐘")
    print(f"台鐵候車：{train['wait_minutes']:.1f} 分鐘")
    print(f"台鐵乘車：{train['ride_minutes']:.1f} 分鐘")
    print(f"台鐵階段合計：{railway_total:.1f} 分鐘")

    print("-" * 68)
    print("轉乘與捷運候車情境")
    print("以下轉乘、捷運候車時間均為研究假設。")

    for index, scenario in enumerate(scenarios, start=1):
        print(
            f"情境 {index}｜"
            f"轉乘 {scenario['transfer_minutes']} 分鐘｜"
            f"捷運候車 {scenario['mrt_wait_minutes']} 分鐘"
        )

        if scenario["mrt_wait_minutes"] == 0:
            print("  理想下限：不計捷運候車時間")

        print(
            f"  預計抵達西門："
            f"{scenario['ximen_arrival_time']}"
        )
        print(
            f"  全程旅行時間："
            f"{scenario['total_minutes']:.1f} 分鐘"
        )


# ============================================================
# 8. 主程式：比較不同出發時間
# ============================================================

def main():
    print("=" * 68)
    print("Mission 15：不同出發時間的大眾運輸旅程比較")
    print("=" * 68)

    print(f"測試出發時間數量：{len(USER_ARRIVAL_TIMES)}")
    print(
        f"每個時間的情境數量："
        f"{len(TRANSFER_TIMES) * len(MRT_WAIT_TIMES)}"
    )

    for user_arrival_time in USER_ARRIVAL_TIMES:
        print_journey_result(user_arrival_time)

    print()
    print("=" * 68)
    print("Mission 15：多出發時間比較完成")
    print("注意：結果是模型估算，不是即時交通預報。")
    print("=" * 68)




def check_journey_result_structure():
    """檢查統一旅程資料結構是否正常運作。"""

    results = get_journey_results_as_dict("08:30:00")

    print("\n" + "=" * 60)
    print("JourneyResult 資料結構檢查")
    print("=" * 60)

    print(f"情境數量：{len(results)}")

    if results:
        first = results[0]

        print(f"情境編號：{first['scenario_id']}")
        print(f"運具類型：{first['mode']}")
        print(f"起點：{first['origin']}")
        print(f"終點：{first['destination']}")
        print(f"使用者開始時間：{first['user_start_time']}")
        print(
            "第一班車出發時間："
            f"{first['first_vehicle_departure_time']}"
        )
        print(f"抵達時間：{first['arrival_time']}")
        print(f"全程時間：{first['total_minutes']} 分鐘")
        print(f"階段數量：{len(first['stages'])}")
        print(f"研究假設數量：{len(first['assumptions'])}")
        print(f"重要時間節點：{first['milestones']}")

    print("=" * 60)





if __name__ == "__main__":
    main()
    check_journey_result_structure()