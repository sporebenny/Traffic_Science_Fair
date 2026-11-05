

import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean


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
    / "transfer_sensitivity_summary.csv"
)


def load_data():
    """讀取情境資料並檢查必要欄位。"""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"找不到輸入資料：{INPUT_FILE}"
        )

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    required = {
        "scenario_id",
        "user_start_time",
        "total_minutes",
        "stage_4_minutes",
        "stage_5_minutes",
    }

    if not rows:
        raise ValueError("輸入 CSV 沒有資料。")

    missing = required - set(rows[0].keys())

    if missing:
        raise ValueError(
            "輸入 CSV 缺少必要欄位："
            + ", ".join(sorted(missing))
        )

    for row in rows:
        try:
            row["total_minutes"] = float(
                row["total_minutes"]
            )
            row["stage_4_minutes"] = float(
                row["stage_4_minutes"]
            )
            row["stage_5_minutes"] = float(
                row["stage_5_minutes"]
            )
        except (TypeError, ValueError) as error:
            raise ValueError(
                f"情境 {row['scenario_id']} 有無效的時間數值。"
            ) from error

    return rows


def summarize_factor(rows, factor_name, factor_key):
    """固定出發時間，分別計算某個因素各設定值的結果。"""

    groups = defaultdict(list)

    for row in rows:
        key = (
            row["user_start_time"],
            row[factor_key],
        )
        groups[key].append(row)

    results = []

    for (start_time, factor_value), scenarios in sorted(
        groups.items()
    ):
        totals = [
            row["total_minutes"]
            for row in scenarios
        ]

        results.append({
            "analysis_type": factor_name,
            "user_start_time": start_time,
            "factor_minutes": factor_value,
            "scenario_count": len(scenarios),
            "average_total_minutes": round(mean(totals), 2),
            "minimum_total_minutes": round(min(totals), 2),
            "maximum_total_minutes": round(max(totals), 2),
        })

    # 在同一出發時間、同一因素內，計算相對於最小設定值的平均差。
    by_start = defaultdict(list)

    for result in results:
        by_start[result["user_start_time"]].append(result)

    for start_time, items in by_start.items():
        baseline = min(
            items,
            key=lambda item: item["factor_minutes"],
        )
        baseline_average = baseline["average_total_minutes"]

        for item in items:
            item["difference_from_lowest_minutes"] = round(
                item["average_total_minutes"] - baseline_average,
                2,
            )

    return results


def main():
    rows = load_data()

    transfer_results = summarize_factor(
        rows,
        "轉乘時間",
        "stage_4_minutes",
    )

    waiting_results = summarize_factor(
        rows,
        "捷運候車時間",
        "stage_5_minutes",
    )

    all_results = transfer_results + waiting_results

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "analysis_type",
        "user_start_time",
        "factor_minutes",
        "scenario_count",
        "average_total_minutes",
        "minimum_total_minutes",
        "maximum_total_minutes",
        "difference_from_lowest_minutes",
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
        writer.writerows(all_results)

    print("=" * 72)
    print("轉乘條件敏感度分析完成")
    print("=" * 72)
    print(f"讀取情境數：{len(rows)}")
    print(f"輸出分析列數：{len(all_results)}")
    print(f"輸出檔案：{OUTPUT_FILE}")
    print("-" * 72)

    for factor_name, results in (
        ("轉乘時間", transfer_results),
        ("捷運候車時間", waiting_results),
    ):
        print(f"\n【{factor_name}】")
        print(
            f"{'抵達時間':<12}"
            f"{'設定(min)':>12}"
            f"{'情境數':>8}"
            f"{'平均總時間':>14}"
            f"{'相對差異':>12}"
        )

        for item in results:
            print(
                f"{item['user_start_time']:<12}"
                f"{item['factor_minutes']:>12.1f}"
                f"{item['scenario_count']:>8}"
                f"{item['average_total_minutes']:>14.2f}"
                f"{item['difference_from_lowest_minutes']:>12.2f}"
            )

    if len(rows) == 27 and len(all_results) == 18:
        print("\n驗收通過：27 個情境、18 列因素分析。")
    else:
        print(
            "\n數量提醒：預期 27 個情境、18 列因素分析；"
            f"實際為 {len(rows)} 個情境、{len(all_results)} 列。"
        )

    print("注意：分析結果反映模型設定，不代表實測交通效應。")
    print("=" * 72)


if __name__ == "__main__":
    main()
