# 中央氣象署(CWA)自動氣象站API整合

本專案整合了中央氣象署的自動氣象站觀測API (O-A0003-001)，用於獲取全台即時氣溫數據。

## 功能特色

- 🔑 安全的API金鑰管理 (從.env檔案讀取)
- 🌡️ 即時氣溫數據獲取
- 📍 支援全台或特定城市查詢
- 📊 數據分析與統計功能
- 💾 CSV格式數據匯出
- 🛡️ 完整的錯誤處理機制

## 安裝依賴

```bash
pip install -r requirements.txt
```

## 設定

1. 在專案根目錄建立 `.env` 檔案
2. 添加您的CWA API金鑰：

```env
CWA_API_KEY=your_api_key_here
```

### 取得CWA API金鑰

1. 前往 [中央氣象署開放資料平台](https://opendata.cwa.gov.tw/)
2. 註冊帳號並申請API金鑰
3. 將金鑰添加至 `.env` 檔案

## 使用方法

### 基本使用

```python
from scripts.cwa_weather_api import CWAWeatherAPI

# 初始化API客戶端
cwa_api = CWAWeatherAPI()

# 獲取全台氣象站數據
df = cwa_api.get_temperature_dataframe()

# 顯示數據
print(df.head())
```

### 特定城市查詢

```python
# 查詢特定城市
cities = ['台北', '台中', '高雄']
df = cwa_api.get_temperature_dataframe(cities)
```

### 保存數據

```python
# 保存為CSV檔案
output_file = cwa_api.save_temperature_data()
print(f"數據已保存至: {output_file}")
```

### 執行範例腳本

```bash
# 執行完整範例
python scripts/example_usage.py

# 執行主要腳本
python scripts/cwa_weather_api.py
```

## 輸出數據格式

API回應包含以下欄位：

| 欄位 | 描述 | 類型 |
|------|------|------|
| station_id | 測站編號 | String |
| station_name | 測站名稱 | String |
| location | 地點名稱 | String |
| latitude | 緯度 | Float |
| longitude | 經度 | Float |
| observed_time | 觀測時間 | DateTime |
| temperature | 氣溫 (°C) | Float |
| humidity | 相對濕度 (%) | Float |
| weather | 天氣狀況 | String |

## API資訊

- **API端點**: `https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001`
- **資料集**: 自動氣象站-觀測資料
- **更新頻率**: 即時更新
- **資料格式**: JSON

## 錯誤處理

腳本包含完整的錯誤處理機制：

- API金鑰缺失檢查
- 網路請求錯誤處理
- JSON解析錯誤處理
- 數據格式驗證
- 個別測站數據錯誤隔離

## 範例輸出

```
正在獲取全台自動氣象站數據...
成功獲取 521 個測站數據
數據時間範圍: 2024-02-24 15:00:00 ~ 2024-02-24 15:00:00

氣溫統計:
平均氣溫: 23.5°C
最高氣溫: 31.2°C
最低氣溫: 12.8°C

前10個測站氣溫數據:
  station_name location  temperature  humidity
        恆春      恆春        29.8      78.5
        台東      台東        28.9      82.1
        花蓮      花蓮        27.6      79.3
        ...
```

## 專案結構

```
spatial-analysis/
├── .env                    # 環境變數 (需自行建立)
├── requirements.txt        # Python依賴
├── README_CWA_API.md      # 說明文件
├── scripts/
│   ├── cwa_weather_api.py # 主要API客戶端
│   └── example_usage.py   # 使用範例
└── outputs/               # 數據輸出目錄
    └── cwa_temperature_data_*.csv
```

## 注意事項

1. **API限制**: 請遵守CWA API的使用限制與規範
2. **資料更新**: 氣象數據約每10分鐘更新一次
3. **時區**: 所有時間均為台灣標準時間 (UTC+8)
4. **網路連線**: 需要穩定的網路連線以獲取即時數據

## 授權

本專案遵循MIT授權條款。中央氣象署開放資料的使用請遵循其官方授權規範。
