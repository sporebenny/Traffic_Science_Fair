


import csv
import json
from pathlib import Path

from experiments.railway_to_mrt_transfer_model import (
    USER_ARRIVAL_TIMES,
    calculate_journey_results,
)


# ============================================================
# 1. 設定專案路徑與輸出位置
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "transit"
    / "public_transport_scenarios.csv"
)


# ============================================================
# 2. 資料轉換工具
# ============================================================

def value_to_text(value):
    """將時間、數字或其他值轉成適合寫入 CSV 的文字。"""

    if value is None:
        return ""

    return str(value)


def get_stage_name(stage):
    """從旅程階段資料中取得階段名稱。"""

    if not isinstance(stage, dict):
        return ""

    for key in ("name", "stage", "label", "title"):
        if stage.get(key) is not None:
            return str(stage[key])

    return ""


def get_stage_minutes(stage):
    """取得單一旅程階段的時間。"""

    if not isinstance(stage, dict):
        return ""

    for key in ("minutes", "duration_minutes"):
        if stage.get(key) is not None:
            return stage[key]

    return ""


def to_json_text(value):
    """將階段細節、里程碑或假設轉成 JSON 文字。"""

    return json.dumps(
        value,
        ensure_ascii=False,
        default=str,
    )


# ============================================================
# 3. 將單一情境轉成 CSV 資料列
# ============================================================

def build_csv_row(result):
    """將一個 JourneyResult 轉成一列 CSV 資料。"""

    stages = getattr(result, "stages", []) or []
    milestones = getattr(result, "milestones", []) or []
    assumptions = getattr(result, "assumptions", []) or []

    row = {
        "scenario_id": value_to_text(
            getattr(result, "scenario_id", "")
        ),
        "mode": value_to_text(
            getattr(result, "mode", "")
        ),
        "origin": value_to_text(
            getattr(result, "origin", "")
        ),
        "destination": value_to_text(
            getattr(result, "destination", "")
        ),
        "user_start_time": value_to_text(
            getattr(result, "user_start_time", "")
        ),
        "first_vehicle_departure": value_to_text(
            getattr(result, "first_vehicle_departure", "")
        ),
        "arrival_time": value_to_text(
            getattr(result, "arrival_time", "")
        ),
        "total_minutes": value_to_text(
            getattr(result, "total_minutes", "")
        ),
        "stage_count": len(stages),
        "stages_json": to_json_text(stages),
        "milestones_json": to_json_text(milestones),
        "assumptions_json": to_json_text(assumptions),
    }

    # 將各階段名稱與分鐘數拆成獨立欄位。
    for index in range(6):
        stage_number = index + 1

        if index < len(stages):
            stage = stages[index]
            stage_name = get_stage_name(stage)
            stage_minutes = get_stage_minutes(stage)
        else:
            stage_name = ""
            stage_minutes = ""

        row[f"stage_{stage_number}_name"] = stage_name
        row[f"stage_{stage_number}_minutes"] = stage_minutes

    return row


# ============================================================
# 4. 輸出全部大眾運輸情境
# ============================================================

def export_results():
    """產生大眾運輸情境 CSV，並回報驗收結果。"""


    results = []

    for user_arrival_time in USER_ARRIVAL_TIMES:
        journey_results = calculate_journey_results(
            user_arrival_time
        )
        results.extend(journey_results)


    fieldnames = [
        "scenario_id",
        "mode",
        "origin",
        "destination",
        "user_start_time",
        "first_vehicle_departure",
        "arrival_time",
        "total_minutes",
        "stage_count",
    ]

    for index in range(1, 7):
        fieldnames.extend([
            f"stage_{index}_name",
            f"stage_{index}_minutes",
        ])

    fieldnames.extend([
        "stages_json",
        "milestones_json",
        "assumptions_json",
    ])

    rows = [
        build_csv_row(result)
        for result in results
    ]

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(rows)

    print("=" * 60)
    print("大眾運輸情境資料匯出完成")
    print("=" * 60)
    print(f"輸出檔案：{OUTPUT_FILE}")
    print(f"情境筆數：{len(rows)}")
    print(f"欄位數量：{len(fieldnames)}")

    if len(rows) == 27:
        print("情境數量驗收：通過（27 筆）")
    else:
        print(
            f"情境數量提醒：預期 27 筆，"
            f"實際產生 {len(rows)} 筆。"
        )

    if all(row["scenario_id"] for row in rows):
        print("情境編號檢查：通過")
    else:
        print("情境編號檢查：發現空白編號")

    print("=" * 60)


if __name__ == "__main__":
    try:
        export_results()
    except (OSError, ValueError, TypeError, AttributeError) as error:
        print(f"資料匯出失敗：{error}")
        raise
