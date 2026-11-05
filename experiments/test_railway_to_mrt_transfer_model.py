


import unittest
from unittest.mock import patch
from datetime import datetime

from experiments import railway_to_mrt_transfer_model as model


class TestRailwayToMRTTransferModel(unittest.TestCase):

    def setUp(self):
        """建立固定的臺鐵測試資料，避免依賴真實時刻表。"""
        self.train = {
            "train_no": "TEST001",
            "departure": "08:16:00",
            "arrival": "08:57:00",
            "access_minutes": 10,
            "wait_minutes": 6,
            "ride_minutes": 41,
        }

    def test_mrt_ready_time(self):
        """臺鐵 08:57 抵達，轉乘 3 分鐘，應於 09:00 可候車。"""
        result = model.calculate_mrt_ready_time("08:57:00", 3)
        self.assertEqual(result, datetime.strptime("09:00:00", "%H:%M:%S"))

    def test_ximen_arrival_time(self):
        """09:00 可候車，捷運候車 3 分鐘、搭乘 2 分鐘，09:05 抵達。"""
        ready_time = datetime.strptime("09:00:00", "%H:%M:%S")
        result = model.calculate_ximen_arrival_time(ready_time, 3, 2)
        self.assertEqual(result.strftime("%H:%M:%S"), "09:05:00")

    def test_total_journey_minutes(self):
        """10 + 6 + 41 + 3 + 3 + 2 = 65 分鐘。"""
        result = model.calculate_total_minutes(
            self.train,
            transfer_minutes=3,
            mrt_wait_minutes=3,
            mrt_ride_minutes=2,
        )
        self.assertEqual(result, 65)

    @patch.object(model, "get_next_train")
    def test_nine_scenarios(self, mock_get_next_train):
        """每個抵達時間都應產生 3 × 3 = 9 種情境。"""
        mock_get_next_train.return_value = self.train

        train, scenarios = model.calculate_journey_scenarios("08:00:00")

        self.assertEqual(train, self.train)
        self.assertEqual(len(scenarios), 9)

        for scenario in scenarios:
            expected_total = (
                self.train["access_minutes"]
                + self.train["wait_minutes"]
                + self.train["ride_minutes"]
                + scenario["transfer_minutes"]
                + scenario["mrt_wait_minutes"]
                + scenario["mrt_ride_minutes"]
            )
            self.assertEqual(scenario["total_minutes"], expected_total)

    @patch.object(model, "get_next_train")
    def test_no_available_train(self, mock_get_next_train):
        """沒有可搭乘班次時，應回傳 (None, [])。"""
        mock_get_next_train.return_value = None

        train, scenarios = model.calculate_journey_scenarios("08:00:00")

        self.assertIsNone(train)
        self.assertEqual(scenarios, [])

    def test_invalid_arrival_time(self):
        """錯誤的使用者抵達時間應觸發 ValueError。"""
        with self.assertRaises(ValueError):
            model.calculate_journey_scenarios("25:61:00")


if __name__ == "__main__":
    unittest.main(verbosity=2)


