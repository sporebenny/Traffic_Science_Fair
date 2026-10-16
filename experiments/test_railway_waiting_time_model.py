
import unittest

from experiments.railway_waiting_time_model import (
    calculate_waiting_time,
    find_next_train,
    convert_time,
)


class TestRailwayWaitingTimeModel(unittest.TestCase):

    def test_normal_waiting_time(self):
        """08:10 等到 08:16，應為 6 分鐘。"""
        ready_time = convert_time("08:10:00")
        wait = calculate_waiting_time(ready_time, "08:16:00")
        self.assertEqual(wait, 6)

    def test_midnight_waiting_time(self):
        """23:50 等到隔日 00:10，應為 20 分鐘。"""
        ready_time = convert_time("23:50:00")
        wait = calculate_waiting_time(ready_time, "00:10:00")
        self.assertEqual(wait, 20)

    def test_find_next_train_unsorted_data(self):
        """班次未排序時，應找到等待時間最短的列車。"""
        trains = [
            {
                "train_no": "A",
                "departure": "08:30:00",
                "arrival": "09:00:00",
                "travel_minutes": 30,
            },
            {
                "train_no": "B",
                "departure": "08:15:00",
                "arrival": "08:45:00",
                "travel_minutes": 30,
            },
            {
                "train_no": "C",
                "departure": "08:20:00",
                "arrival": "08:50:00",
                "travel_minutes": 30,
            },
        ]

        ready_time = convert_time("08:10:00")
        result = find_next_train(trains, ready_time)
        self.assertEqual(result["train_no"], "B")

    def test_no_train_data(self):
        """沒有班次資料時，應回傳 None。"""
        result = find_next_train([], convert_time("08:10:00"))
        self.assertIsNone(result)

    def test_invalid_time_format(self):
        """錯誤的時間格式應觸發 ValueError。"""
        with self.assertRaises(ValueError):
            convert_time("25:61:00")


if __name__ == "__main__":
    unittest.main(verbosity=2)
