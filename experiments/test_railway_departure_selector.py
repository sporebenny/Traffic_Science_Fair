
import unittest

from experiments.railway_departure_selector import (
    parse_time,
    select_next_train,
)


class TestRailwayDepartureSelector(unittest.TestCase):

    def setUp(self):
        self.trains = [
            {
                "train_no": "4154",
                "departure": "07:30:00",
                "arrival": "08:12:00",
                "travel_minutes": "42",
            },
            {
                "train_no": "1136",
                "departure": "08:16:00",
                "arrival": "08:57:00",
                "travel_minutes": "41",
            },
            {
                "train_no": "1140",
                "departure": "09:00:00",
                "arrival": "09:42:00",
                "travel_minutes": "42",
            },
        ]

    def test_parse_time_with_seconds(self):
        result = parse_time("07:30:00")
        self.assertEqual(result.strftime("%H:%M"), "07:30")

    def test_parse_time_without_seconds(self):
        result = parse_time("07:30")
        self.assertEqual(result.strftime("%H:%M"), "07:30")

    def test_select_train_at_exact_arrival_time(self):
        result = select_next_train(self.trains, "07:30")

        self.assertEqual(result["train_no"], "4154")
        self.assertEqual(result["waiting_minutes"], 0)

    def test_select_next_train(self):
        result = select_next_train(self.trains, "08:15")

        self.assertEqual(result["train_no"], "1136")
        self.assertEqual(result["waiting_minutes"], 1)

    def test_no_available_train(self):
        result = select_next_train(self.trains, "23:00")

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()

    