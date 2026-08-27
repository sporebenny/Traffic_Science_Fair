


def calculate_travel_time(distance_m, speed_kmh):
    """
    計算道路行駛時間

    distance_m : 道路長度（公尺）
    speed_kmh  : 行駛速度（公里/小時）

    return     : 行駛時間（秒）
    """

    speed_ms = speed_kmh * 1000 / 3600

    travel_time = distance_m / speed_ms

    return travel_time



def get_congestion_speed(speed_kmh, congestion_level):
    """
    根據壅塞程度調整道路速度

    speed_kmh       : 正常道路速度（km/h）
    congestion_level: normal / moderate / severe

    return          : 壅塞後速度（km/h）
    """

    congestion_factors = {
        "normal": 1.0,
        "moderate": 0.7,
        "severe": 0.4
    }

    factor = congestion_factors[congestion_level]

    return speed_kmh * factor


def get_congestion_travel_time(distance_m, speed_kmh, congestion_level):
    """
    計算特定壅塞程度下的道路行駛時間

    distance_m       : 道路長度（公尺）
    speed_kmh        : 正常道路速度（km/h）
    congestion_level : normal / moderate / severe

    return           : 行駛時間（秒）
    """

    congestion_speed = get_congestion_speed(
        speed_kmh,
        congestion_level
    )

    travel_time = calculate_travel_time(
        distance_m,
        congestion_speed
    )

    return travel_time

def calculate_edge_travel_time(edge_data, congestion_level):
    """
    根據 Graph Edge 資料計算壅塞後行駛時間

    edge_data       : Graph Edge 的 attributes
    congestion_level: normal / moderate / severe

    return          : 行駛時間（秒）
    """

    distance_m = edge_data["length"]
    speed_kmh = get_edge_speed(edge_data)

    return get_congestion_travel_time(
        distance_m,
        speed_kmh,
        congestion_level
    )




def get_edge_speed(edge_data):
    """
    從 Graph Edge 取得道路正常速度。

    如果 OSM 有 maxspeed，優先使用。
    如果 maxspeed 缺失或無法直接解析，
    則依 highway 類型使用預設速度。
    """

    default_speeds = {
        "motorway": 100,
        "trunk": 80,
        "primary": 60,
        "secondary": 50,
        "tertiary": 40,
        "residential": 30,
        "unclassified": 30,
        "service": 20
    }

    # -------------------------
    # 1. 優先嘗試取得 maxspeed
    # -------------------------

    maxspeed = edge_data.get("maxspeed")

    if maxspeed is not None:

        if isinstance(maxspeed, list):
            maxspeed = maxspeed[0]

        try:
            return float(maxspeed)
        except (ValueError, TypeError):
            pass

    # -------------------------
    # 2. maxspeed 無法使用
    #    → 根據 highway 判斷
    # -------------------------

    highway = edge_data.get("highway", "unclassified")

    if isinstance(highway, list):
        highway = highway[0]

    return default_speeds.get(highway, 30)



def calculate_edge_travel_time(edge_data, congestion_level):
    """
    根據 Graph Edge 資料計算壅塞後行駛時間

    edge_data       : Graph Edge attributes
    congestion_level: normal / moderate / severe

    return          : 行駛時間（秒）
    """

    distance_m = float(edge_data["length"])
    speed_kmh = get_edge_speed(edge_data)

    return get_congestion_travel_time(
        distance_m,
        speed_kmh,
        congestion_level
    )


def apply_congestion_to_graph(G, congestion_level):
    """
    將指定壅塞程度下的 Travel Time
    套用到 Graph 的所有 Edge。
    """

    for u, v, k, data in G.edges(keys=True, data=True):

        data["travel_time"] = calculate_edge_travel_time(
            data,
            congestion_level
        )

    return G




