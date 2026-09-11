


import requests
from pathlib import Path


# 官方資料來源
url = "https://ods.railway.gov.tw/tra-ods-web/ods/download/dataResource/0518b833e8964d53bfea3f7691aea0ee"

# 原始資料儲存位置
output_path = Path("data/transit/raw/taiwan_railway_stations_raw.json")


print("開始下載臺鐵車站基本資料...")

response = requests.get(url, timeout=30)

print("HTTP 狀態碼:", response.status_code)

response.raise_for_status()

output_path.parent.mkdir(parents=True, exist_ok=True)

output_path.write_text(
    response.text,
    encoding="utf-8"
)

print("下載完成！")
print("原始資料位置:", output_path)
print("資料大小:", output_path.stat().st_size, "bytes")
