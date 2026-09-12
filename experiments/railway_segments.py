import pandas as pd
from math import radians, sin, cos, sqrt, atan2


# ==========================================
# 1. 計算兩個車站之間的直線距離
# ==========================================

def calculate_distance(lat1, lon1, lat2, lon2):

    earth_radius = 6371.0

    lat1 = radians(lat1)
    lat2 = radians(lat2)

    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)

    a = (
        sin(delta_lat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(delta_lon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = earth_radius * c

    return distance


# ==========================================
# 2. 讀取研究用車站資料
# ==========================================

file_path = "data/transit/stations.csv"

stations = pd.read_csv(file_path)


# ==========================================
# 3. 找出桃園與臺北
# ==========================================

start_station = "桃園"
end_station = "臺北"


start_index = stations[
    stations["station_name"] == start_station
].index[0]


end_index = stations[
    stations["station_name"] == end_station
].index[0]


# ==========================================
# 4. 建立桃園 → 臺北站序
# ==========================================

if start_index < end_index:

    route_stations = stations.loc[
        start_index:end_index
    ]

else:

    route_stations = stations.loc[
        end_index:start_index
    ].iloc[::-1]


route_stations = route_stations.reset_index(drop=True)


# ==========================================
# 5. 建立鐵路區間
# ==========================================

segments = []

total_distance = 0


for i in range(len(route_stations) - 1):

    start = route_stations.iloc[i]
    end = route_stations.iloc[i + 1]


    # 計算兩站之間的直線距離
    distance = calculate_distance(
        start["latitude"],
        start["longitude"],
        end["latitude"],
        end["longitude"]
    )


    # 建立區間資料
    segment = {
        "segment_number": i + 1,
        "start_station": start["station_name"],
        "end_station": end["station_name"],
        "distance_km": distance
    }


    segments.append(segment)

    total_distance = total_distance + distance


# ==========================================
# 6. 顯示結果
# ==========================================

print("桃園 → 臺北鐵路區間")
print("----------------------------------------")


for segment in segments:

    print(
        segment["segment_number"],
        segment["start_station"],
        "→",
        segment["end_station"],
        "距離:",
        round(segment["distance_km"], 3),
        "km"
    )


print("----------------------------------------")

print("區間數量:", len(segments))

print(
    "總直線距離:",
    round(total_distance, 3),
    "km"
)

