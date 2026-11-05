

import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean


# ============================================================
# 1. 專案路徑
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "transit"
    / "public_transport_scenarios.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "transit"
    / "public_transport_summary.csv"
)


# ============================================================
# 2. 讀取情境資料
# ============================================================

def load_scenarios():
    """讀取已匯出的 27 種大眾運輸情境。"""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"找不到情境資料：{INPUT_FILE}"
        )

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)
        required = {
            "scenario_id",
            "user_start_time",
            "arrival_time",
            "total_minutes",
        }

        if reader.fieldnames is None:
            raise ValueError("CSV 缺少欄位標題。")

        missing = required - set(reader.fieldnames)

        if missing:
            raise ValueError(
                "CSV 缺少必要欄位："
                + ", ".join(sorted(missing))
            )

        rows = list(reader)

    if not rows:
        raise ValueError("CSV 沒有情境資料。")

    for row in rows:
        try:
            row["total_minutes"] = float(
                row["total_minutes"]
            )
        except (ValueError, TypeError) as error:
            raise ValueError(
                f"情境 {row.get('scenario_id', '')} "
                "的 total_minutes 不是有效數字。"
            ) from error

    return rows


# ============================================================
# 3. 依使用者抵達車站時間分組
# ============================================================

def analyze_scenarios(rows):
    """計算各出發時間的統計結果與分段平均時間。"""

    groups = defaultdict(list)

    for row in rows:
        groups[row["user_start_time"]].append(row)

    summaries = []

    for start_time in sorted(groups):
        scenarios = groups[start_time]

        fastest = min(
            scenarios,
            key=lambda row: row["total_minutes"],
        )

        slowest = max(
            scenarios,
            key=lambda row: row["total_minutes"],
        )

        durations = [
            row["total_minutes"]
            for row in scenarios
        ]

        summary = {
            "user_start_time": start_time,
            "scenario_count": len(scenarios),
            "fastest_minutes": min(durations),
            "average_minutes": mean(durations),
            "slowest_minutes": max(durations),
            "time_range_minutes": (
                max(durations) - min(durations)
            ),
            "fastest_scenario_id": fastest["scenario_id"],
            "fastest_arrival_time": fastest["arrival_time"],
            "slowest_scenario_id": slowest["scenario_id"],
            "slowest_arrival_time": slowest["arrival_time"],
        }

        # 計算六個旅程階段各自的平均時間。
        for index in range(1, 7):
            minutes_key = f"stage_{index}_minutes"
            name_key = f"stage_{index}_name"

            stage_values = []

            for row in scenarios:
                value = row.get(minutes_key, "").strip()

                if value:
                    try:
                        stage_values.append(float(value))
                    except ValueError as error:
                        raise ValueError(
                            f"{row['scenario_id']} 的 "
                            f"{minutes_key} 不是有效數字。"
                        ) from error

            stage_names = [
                row.get(name_key, "").strip()
                for row in scenarios
                if row.get(name_key, "").strip()
            ]

            summary[f"stage_{index}_name"] = (
                stage_names[0] if stage_names else ""
            )

            summary[f"stage_{index}_average_minutes"] = (
                round(mean(stage_values), 2)
                if stage_values
                else ""
            )

        summaries.append(summary)

    return summaries


# ============================================================
# 4. 輸出分析表
# ============================================================

def export_summary(summaries):
    """將統計結果寫入新的 CSV。"""

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "user_start_time",
        "scenario_count",
        "fastest_minutes",
        "average_minutes",
        "slowest_minutes",
        "time_range_minutes",
        "fastest_scenario_id",
        "fastest_arrival_time",
        "slowest_scenario_id",
        "slowest_arrival_time",
    ]

    for index in range(1, 7):
        fieldnames.extend([
            f"stage_{index}_name",
            f"stage_{index}_average_minutes",
        ])

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
        writer.writerows(summaries)


# ============================================================
# 5. 顯示分析結果
# ============================================================

def main():
    rows = load_scenarios()
    summaries = analyze_scenarios(rows)

    export_summary(summaries)

    print("=" * 72)
    print("大眾運輸情境分析完成")
    print("=" * 72)
    print(f"原始情境數：{len(rows)}")
    print(f"分析組數：{len(summaries)}")
    print(f"分析表：{OUTPUT_FILE}")
    print("-" * 72)

    print(
        f"{'抵達車站時間':<16}"
        f"{'情境數':>6}"
        f"{'最快(min)':>12}"
        f"{'平均(min)':>12}"
        f"{'最慢(min)':>12}"
        f"{'差距(min)':>12}"
    )

    for item in summaries:
        print(
            f"{item['user_start_time']:<16}"
            f"{item['scenario_count']:>6}"
            f"{item['fastest_minutes']:>12.2f}"
            f"{item['average_minutes']:>12.2f}"
            f"{item['slowest_minutes']:>12.2f}"
            f"{item['time_range_minutes']:>12.2f}"
        )

    print("-" * 72)

    if len(rows) == 27 and len(summaries) == 3:
        print("驗收通過：27 個情境已分成 3 組完成分析。")
    else:
        print(
            "數量提醒：預期 27 個情境、3 組分析；"
            f"實際為 {len(rows)} 個情境、"
            f"{len(summaries)} 組。"
        )

    print("注意：以上為模型情境結果，不代表實測交通時間。")
    print("=" * 72)


if __name__ == "__main__":
    main()
