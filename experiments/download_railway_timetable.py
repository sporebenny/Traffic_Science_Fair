import json
import os
import requests


# ==========================================
# 1. 臺鐵官方 JSON 時刻表清單
# ==========================================

list_url = (
    "https://ods.railway.gov.tw/"
    "tra-ods-web/ods/download/dataResource/"
    "railway_schedule/JSON/list"
)


# ==========================================
# 2. 要下載的日期
# ==========================================

target_date = "20260912"


# ==========================================
# 3. 原始資料儲存位置
# ==========================================

output_path = "data/transit/raw/railway_timetable_raw.json"


# ==========================================
# 4. 建立資料夾
# ==========================================

output_directory = os.path.dirname(output_path)

if not os.path.exists(output_directory):

    os.makedirs(output_directory)


# ==========================================
# 5. 讀取官方檔案清單
# ==========================================

print("開始讀取臺鐵官方時刻表清單...")
print("----------------------------------------")

response = requests.get(
    list_url,
    timeout=30
)

print("清單 HTTP 狀態碼:", response.status_code)

if response.status_code != 200:

    print("無法取得官方時刻表清單。")
    raise SystemExit


# ==========================================
# 6. 尋找指定日期的檔案
# ==========================================

print("尋找日期:", target_date)

file_url = None

for line in response.text.splitlines():

    if target_date + ".json" in line:

        print("找到目標檔案:", target_date + ".json")

        # 從 HTML 找出 href
        start_text = 'href="'
        start_index = line.find(start_text)

        if start_index != -1:

            start_index = start_index + len(start_text)

            end_index = line.find('"', start_index)

            if end_index != -1:

                file_url = line[start_index:end_index]

        break


# ==========================================
# 7. 確認是否找到
# ==========================================

if file_url is None:

    print("找不到指定日期的時刻表檔案。")
    raise SystemExit


print("官方檔案連結:", file_url)


# ==========================================
# 8. 如果是相對路徑，補上官方網域
# ==========================================

if file_url.startswith("/"):

    file_url = (
        "https://ods.railway.gov.tw"
        + file_url
    )


print("實際下載網址:", file_url)


# ==========================================
# 9. 開始下載
# ==========================================

print("----------------------------------------")
print("開始下載臺鐵時刻表...")

response = requests.get(
    file_url,
    timeout=30
)

print("下載 HTTP 狀態碼:", response.status_code)


# ==========================================
# 10. 確認下載成功
# ==========================================

if response.status_code != 200:

    print("時刻表下載失敗。")
    raise SystemExit


# ==========================================
# 11. 解析 JSON
# ==========================================

data = response.json()

print("JSON 解析成功！")
print("資料型態:", type(data))


# ==========================================
# 12. 保存原始資料
# ==========================================

with open(
    output_path,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        data,
        file,
        ensure_ascii=False,
        indent=2
    )


# ==========================================
# 13. 完成
# ==========================================

print("----------------------------------------")
print("臺鐵時刻表下載完成！")
print("儲存位置:", output_path)

