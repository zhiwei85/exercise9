# ARIA v3.0: The Living Auditor - 動態災害監測系統

**全自動區域受災衝擊評估系統（動態監測版）**

整合 Week 3-4 的避難所風險評估資料，結合即時雨量監測，建立能回答「現在哪裡最危險？」的動態監測儀表板。

## 🚀 快速開始

### 1. 環境設置
```bash
# 安裝依賴套件
pip install -r requirements.txt

# 設定環境變數（複製 .env.example 到 .env）
cp .env.example .env
# 編輯 .env 檔案，設定你的 API keys
```

### 2. 執行 ARIA v3.0
```bash
# 啟動 Jupyter Notebook
jupyter notebook ARIA_v3.ipynb

# 或使用 JupyterLab
jupyter lab ARIA_v3.ipynb
```

### 3. 查看結果
- 執行完所有 cell 後，會產生 `ARIA_v3_Fungwong.html`
- 在瀏覽器中開啟 HTML 檔案即可查看互動式地圖

## 📋 系統架構

### 核心功能模組

1. **模式切換器 (Mode Switcher)**
   - LIVE 模式：呼叫 CWA O-A0002-001 API 取得即時雨量
   - SIMULATION 模式：載入鳳凰颱風歷史資料
   - Fallback 機制：API 失敗時自動切換到本地資料

2. **資料標準化 (normalize_cwa_json)**
   - 統一處理 CWA API 和 CoLife 歷史資料格式
   - 自動識別座標格式（TWD67 vs WGS84）
   - 過濾無效資料（-998 缺測值）

3. **空間分析引擎**
   - CRS 轉換：EPSG:4326 → EPSG:3826
   - 雨量站影響範圍 buffer（5km）
   - 空間連接：找出暴雨影響範圍內的避難所

4. **動態風險評估**
   - CRITICAL：時雨量 > 80mm 影響範圍內的避難所
   - URGENT：時雨量 > 40mm 且地形風險 HIGH
   - WARNING：時雨量 > 40mm 或地形風險 HIGH
   - SAFE：其餘

5. **互動式視覺化**
   - Folium 地圖與多圖層控制
   - 雨量站 CircleMarker（4級顏色分類）
   - 避難所動態風險標示
   - HeatMap 雨量分佈圖
   - 詳細資訊 Popup

## 🛠️ 技術規格

### 資料來源
- **向量資料**：Week 3 避難所河川距離、Week 4 地形風險評估
- **雨量資料**：CWA O-A0002-001 API 或 CoLife 歷史資料庫
- **測試情境**：2025 年鳳凰颱風（Typhoon Fung-wong）

### 座標系統
- **輸入**：EPSG:4326 (WGS84)
- **分析**：EPSG:3826 (TWD97)
- **輸出**：EPSG:4326 (Folium 地圖)

### 環境變數設定
```bash
APP_MODE=SIMULATION              # LIVE 或 SIMULATION
CWA_API_KEY=your-key-here        # CWA API 金鑰
SIMULATION_DATA=data/scenarios/fungwong_202511.json
TARGET_COUNTY=花蓮縣              # 目標縣市
```

## 🧠 AI 診斷日誌

### 解決的技術問題

#### 1. 「Folium 地圖上經緯度填反（lat/lon 順序）」

**問題描述**：初期建立 Folium Marker 時，發現地圖標點位置偏移嚴重，部分點甚至出現在海上。

**診斷過程**：
1. 檢查 GeoDataFrame 的 geometry 欄位確認座標正確
2. 比對原始經緯度與 Google Maps 位置
3. 發現 Folium.Marker() 參數順序為 `[lat, lon]`，但 geometry 為 `[lon, lat]`

**解決方案**：
```python
# 錯誤寫法
folium.Marker(location=[shelter.geometry.x, shelter.geometry.y])  # [lon, lat]

# 正確寫法  
folium.Marker(location=[shelter.geometry.y, shelter.geometry.x])  # [lat, lon]
```

**學習心得**：GIS 函式庫間的座標順序不一致是常見陷阱，Folium 遵循 Web 標準 `[lat, lon]`，而 GeoPandas geometry 使用 `[lon, lat]`。

#### 2. 「CWA API 回傳 -998 導致地圖顏色異常」

**問題描述**：部分雨量站顯示為異常大的圓圈，檢查發現時雨量值為 -998。

**診斷過程**：
1. 列印雨量資料統計，發現最小值為 -998
2. 查詢 CWA API 文件，確認 -998 為缺測值標記
3. 檢查顏色分類邏輯，發現負值被歸類為最高等級

**解決方案**：
```python
# 在 normalize_cwa_json() 中加入過濾
if rain_1hr == -998 or rain_1hr < 0:
    continue  # 跳過無效資料

# 並在建立 CircleMarker 前再次確認
if station['rain_1hr'] <= 0:
    continue  # 避免零或負值影響視覺化
```

**學習心得**：氣象資料的品質檢查至关重要，需要在資料載入和視覺化兩個階段都加入防呆機制。

#### 3. 「sjoin 結果為空（CRS 未對齊）」

**問題描述**：執行 `gpd.sjoin()` 後結果為空的 GeoDataFrame，但視覺檢查發現雨量站和避難所位置明顯重疊。

**診斷過程**：
1. 分別列印兩個 GeoDataFrame 的 CRS
2. 發現雨量站仍為 EPSG:4326，避難所已轉為 EPSG:3826
3. 意識到 buffer 操作前未確保 CRS 一致性

**解決方案**：
```python
# 加入 CRS 檢查機制
assert str(shelters.crs) == str(rain_stations.crs), "CRS MISMATCH!"

# 在建立 buffer 前確保轉換
rainfall_gdf = rainfall_gdf.to_crs('EPSG:3826')
shelters_gdf = shelters_gdf.to_crs('EPSG:3826')
```

**學習心得**：空間分析前務必進行 CRS 三重檢查：原始資料、分析過程、輸出結果。加入 assert 斷言可以在開發階段快速發現問題。

#### 4. 「HeatMap 在山區有盲區（測站分佈不均）」

**問題描述**：HeatMap 在山區顯示為空白，但實際上該區域可能有降雨。

**診斷過程**：
1. 檢查雨量站分佈，發現山區測站密度較低
2. 分析 CoLife 歷史資料，確認山區確實缺少測站
3. 測試不同的 HeatMap 參數（radius, blur）

**解決方案**：
```python
# 調整 HeatMap 參數以覆蓋更大範圍
HeatMap(
    heat_data,
    radius=20,    # 增加影響半徑
    blur=15,      # 增加模糊程度
    max_zoom=17,  # 設定最大縮放層級
)
```

**學習心得**：視覺化參數需要根據資料分佈特性調整，山區測站稀少是客觀限制，可透過調整視覺化參數部分補償。

## 📊 評量結果對應

| 評量項目 | 實作狀態 | 說明 |
|---------|---------|------|
| Mode Switcher + API 呼叫/fallback | ✅ 完成 | 支援 LIVE/SIMULATION 雙模式，含錯誤處理 |
| 鳳凰颱風空間疊合 + 動態風險分級 | ✅ 完成 | 5km buffer + sjoin + 四級風險分類 |
| Folium 互動地圖品質 | ✅ 完成 | 多圖層、Popup、HeatMap、LayerControl |
| 專業規範（.env + .gitignore + README） | ✅ 完成 | 完整的專業開發環境設定 |
| Bonus: Gemini SDK 整合 | ⚙️ 可選 | 程式碼已準備，需設定 GEMINI_API_KEY |

## 🎯 使用案例

### 即時監測模式
```bash
# 設定 .env
APP_MODE=LIVE
CWA_API_KEY=your-real-api-key
```

### 歷史重演模式
```bash
# 設定 .env  
APP_MODE=SIMULATION
SIMULATION_DATA=data/scenarios/fungwong_202511.json
```

### AI 顧問模式（加分題）
```bash
# 在 .env 中加入
GEMINI_API_KEY=your-gemini-api-key
```

## 📁 檔案結構

```
homework5/
├── ARIA_v3.ipynb              # 主要分析 Notebook
├── ARIA_v3_Fungwong.html      # 輸出的互動式地圖
├── requirements.txt            # Python 套件依賴
├── .env                       # 環境變數設定（不上傳 Git）
├── .gitignore                 # Git 忽略檔案設定
├── README.md                  # 本檔案
└── data/
    └── scenarios/
        └── fungwong_202511.json # 鳳凰颱風歷史資料
```

## 🤝 貢獻與回饋

這個系統展示了如何將學術理論轉化為實際的防災應用。歡迎提供改進建議或回報問題。

---

**"A monitoring system that works in the sun is a toy. A system that survives Typhoon Fung-wong is a tool."**
