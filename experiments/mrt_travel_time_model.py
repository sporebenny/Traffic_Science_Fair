from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

MRT_TRAVEL_TIME_FILE = (
    PROJECT_ROOT
    / "data"
    / "transit"
    / "mrt_travel_times.csv"
)

REQUIRED_COLUMNS = [
    "line",
    "origin_code",
    "origin_name",
    "destination_code",
    "destination_name",
    "direction",
    "travel_minutes",
    "source",
]


def load_mrt_travel_times():
    """Load MRT travel-time records from CSV."""

    if not MRT_TRAVEL_TIME_FILE.exists():
        raise FileNotFoundError(
            f"File not found: {MRT_TRAVEL_TIME_FILE}"
        )

    return pd.read_csv(
        MRT_TRAVEL_TIME_FILE,
        encoding="utf-8"
    )


def validate_mrt_travel_times(data):
    """Validate the MRT travel-time dataset."""

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    if data.empty:
        raise ValueError("Dataset is empty.")

    if data[REQUIRED_COLUMNS].isnull().any().any():
        raise ValueError("Dataset contains empty fields.")

    travel_minutes = pd.to_numeric(
        data["travel_minutes"],
        errors="coerce"
    )

    if travel_minutes.isnull().any():
        raise ValueError("Travel minutes must be numeric.")

    if (travel_minutes <= 0).any():
        raise ValueError(
            "Travel minutes must be greater than zero."
        )

    duplicated = data.duplicated(
        subset=[
            "line",
            "origin_code",
            "destination_code",
            "direction",
        ]
    )

    if duplicated.any():
        raise ValueError("Duplicate MRT route records found.")

    return True


def get_mrt_travel_time(
    origin_code,
    destination_code,
    line=None,
    direction=None,
):
    """Query travel time between two MRT stations."""

    data = load_mrt_travel_times()
    validate_mrt_travel_times(data)

    matches = data[
        (data["origin_code"] == origin_code)
        & (data["destination_code"] == destination_code)
    ]

    if line is not None:
        matches = matches[matches["line"] == line]

    if direction is not None:
        matches = matches[
            matches["direction"] == direction
        ]

    if matches.empty:
        raise ValueError(
            f"No matching route: {origin_code} -> {destination_code}"
        )

    if len(matches) > 1:
        raise ValueError(
            "Multiple matching records. Specify line or direction."
        )

    return int(matches.iloc[0]["travel_minutes"])


if __name__ == "__main__":

    mrt_data = load_mrt_travel_times()

    validate_mrt_travel_times(mrt_data)

    print("MRT travel-time data validation: PASSED")
    print(f"Number of records: {len(mrt_data)}")

    travel_time = get_mrt_travel_time(
        origin_code="BL12",
        destination_code="BL11",
        line="BL",
        direction="往頂埔",
    )

    print(
        "Taipei Main Station -> Ximen Station:",
        f"{travel_time} minutes"
    )
