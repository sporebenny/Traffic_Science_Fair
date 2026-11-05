

from datetime import datetime

from experiments.railway_to_mrt_transfer_model import (
    USER_ARRIVAL_TIMES,
    calculate_journey_scenarios,
)

SECONDS_PER_DAY = 24 * 60 * 60
TOLERANCE_MINUTES = 1.0


def seconds_of_day(time_string):
    """將 HH:MM:SS 轉換為當日秒數。"""
    value = datetime.strptime(time_string, "%H:%M:%S")
    return value.hour * 3600 + value.minute * 60 + value.second


def elapsed_minutes(start_time, end_time):
    """計算兩個時刻之間的經過時間，支援跨午夜。"""
    difference = (
        seconds_of_day(end_time) - seconds_of_day(start_time)
    ) % SECONDS_PER_DAY

    return difference / 60


def main():
    checked_scenarios = 0
    errors = []

    print("=" * 68)
    print("PT-04A：大眾運輸旅程時間軸驗收")
    print("=" * 68)

    for user_start in USER_ARRIVAL_TIMES:
        train, scenarios = calculate_journey_scenarios(user_start)

        if train is None:
            errors.append(
                f"{user_start}：找不到可搭乘的臺鐵班次"
            )
            continue

        for index, scenario in enumerate(scenarios, start=1):
            checked_scenarios += 1

            # 檢查一：出發時刻至西門抵達時刻的經過時間
            timeline_minutes = elapsed_minutes(
                user_start,
                scenario["ximen_arrival_time"],
            )

            expected_total = scenario["total_minutes"]

            if abs(timeline_minutes - expected_total) > TOLERANCE_MINUTES:
                errors.append(
                    f"{user_start} 情境 {index}："
                    f"時間軸經過 {timeline_minutes:.2f} 分鐘，"
                    f"但總時間為 {expected_total:.2f} 分鐘"
                )

            # 檢查二：臺鐵出發至抵達的時間是否符合乘車時間
            train_elapsed = elapsed_minutes(
                scenario["tra_departure"],
                scenario["tra_arrival"],
            )

            expected_ride = scenario["tra_ride_minutes"]

            if abs(train_elapsed - expected_ride) > TOLERANCE_MINUTES:
                errors.append(
                    f"{user_start} 情境 {index}："
                    f"臺鐵時刻表經過 {train_elapsed:.2f} 分鐘，"
                    f"但 CSV 乘車時間為 {expected_ride:.2f} 分鐘"
                )

            # 檢查三：使用者進站並候車後，是否對上臺鐵出發時刻
            expected_departure_elapsed = (
                scenario["access_minutes"]
                + scenario["tra_wait_minutes"]
            )

            actual_departure_elapsed = elapsed_minutes(
                user_start,
                scenario["tra_departure"],
            )

            if abs(
                actual_departure_elapsed - expected_departure_elapsed
            ) > TOLERANCE_MINUTES:
                errors.append(
                    f"{user_start} 情境 {index}："
                    f"出發時間軸為 {actual_departure_elapsed:.2f} 分鐘，"
                    f"但進站加候車為 "
                    f"{expected_departure_elapsed:.2f} 分鐘"
                )

    print(f"檢查情境數：{checked_scenarios}")
    print(f"發現問題數：{len(errors)}")
    print("-" * 68)

    if errors:
        print("驗收結果：未通過")
        for error in errors:
            print(f"- {error}")
    else:
        print("驗收結果：通過")
        print("所有情境的總旅行時間、臺鐵乘車時間")
        print("與臺鐵出發時間軸均在容許誤差內。")

    print("=" * 68)


if __name__ == "__main__":
    main()
