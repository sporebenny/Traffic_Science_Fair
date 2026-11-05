


import unittest

import pandas as pd

from experiments.mrt_travel_time_model import (
    get_mrt_travel_time,
    validate_mrt_travel_times,
)


class TestMRTTravelTimeModel(unittest.TestCase):

    def test_normal_route_query(self):
        """T01: Query an existing MRT route."""

        travel_time = get_mrt_travel_time(
            origin_code="BL12",
            destination_code="BL11",
            line="BL",
            direction="往頂埔",
        )

        self.assertEqual(travel_time, 2)

    def test_nonexistent_station(self):
        """T02: Query a nonexistent station."""

        with self.assertRaises(ValueError):
            get_mrt_travel_time(
                origin_code="BL99",
                destination_code="BL11",
            )

    def test_invalid_direction(self):
        """T03: Query with an incorrect direction."""

        with self.assertRaises(ValueError):
            get_mrt_travel_time(
                origin_code="BL12",
                destination_code="BL11",
                line="BL",
                direction="往南港展覽館",
            )

    def test_missing_required_column(self):
        """T04: Detect missing required columns."""

        data = pd.DataFrame([
            {
                "line": "BL",
                "origin_code": "BL12",
                "destination_code": "BL11",
                "travel_minutes": 2,
            }
        ])

        with self.assertRaises(ValueError):
            validate_mrt_travel_times(data)

    def test_non_numeric_travel_time(self):
        """T05: Reject non-numeric travel time."""

        data = pd.DataFrame([
            {
                "line": "BL",
                "origin_code": "BL12",
                "origin_name": "臺北車站",
                "destination_code": "BL11",
                "destination_name": "西門站",
                "direction": "往頂埔",
                "travel_minutes": "invalid",
                "source": "test",
            }
        ])

        with self.assertRaises(ValueError):
            validate_mrt_travel_times(data)

    def test_duplicate_routes(self):
        """T06: Detect duplicate route records."""

        record = {
            "line": "BL",
            "origin_code": "BL12",
            "origin_name": "臺北車站",
            "destination_code": "BL11",
            "destination_name": "西門站",
            "direction": "往頂埔",
            "travel_minutes": 2,
            "source": "test",
        }

        data = pd.DataFrame([
            record,
            record.copy(),
        ])

        with self.assertRaises(ValueError):
            validate_mrt_travel_times(data)


if __name__ == "__main__":
    unittest.main(verbosity=2)
