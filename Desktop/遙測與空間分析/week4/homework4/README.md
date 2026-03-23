# ARIA v2.0 - 全自動區域受災衝擊評估系統（地形整合版）

## 專案概述

ARIA v2.0 是 Week 3 ARIA 系統的升級版，整合了內政部 20m DEM 地形資料，提供更精準的複合風險評估。系統結合河川距離與地形因子（高程、坡度），評估避難所在極端降雨事件中的受災風險。

## 系統升級亮點

- **Week 3**: 單維度河川距離評估
- **Week 4**: **多維度複合風險評估**（河川 + 地形）
- **新增功能**: 坡度計算、高程分析、Zonal Statistics
- **風險精度**: 從位置評估升級至環境強度評估

## 檔案結構

```
homework4/
├── ARIA_v2.ipynb          # 主分析 Notebook
├── .env                   # 環境變數設定
├── README.md              # 專案說明文件
├── terrain_risk_audit.json # 避難所地形風險審計報告
├── analysis_summary.json  # 分析摘要報告
├── terrain_risk_map.png   # DEM + 避難所風險地圖
└── risk_analysis_charts.png # 風險分析統計圖
```

## 資料來源

### 向量資料
- **水利署河川面**: [WRA Open Data](https://data.wra.gov.tw/Attachment/OpenDataFile/5112_26420/WATER_BODY.shp)
- **消防署避難收容所**: [data.gov.tw](https://data.gov.tw/dataset/73242)
- **國土測繪中心鄉鎮界**: 台灣通用電子地圖

### 網格資料
- **內政部 20m DEM**: [data.gov.tw](https://data.gov.tw/dataset/176927)
- **解析度**: 20m × 20m
- **CRS**: EPSG:3826 (TWD97/TM2)

## 核心功能

### 1. 地形分析
- **坡度計算**: 使用 `np.gradient` 計算坡度（度）
- **Zonal Statistics**: 為每個避難所 500m 緩衝區計算：
  - 平均高程 (mean elevation)
  - 最大坡度 (max slope)  
  - 高程標準差 (std elevation)

### 2. 複合風險評估
```python
風險分級邏輯：
- 極高風險：距河川 < 500m 且 最大坡度 > 30°
- 高風險：距河川 < 500m 或 最大坡度 > 30°
- 中風險：距河川 < 1000m 且 平均高程 < 50m
- 低風險：其餘
```

### 3. 視覺化輸出
- **DEM Hillshade 地圖**: 疊加避難所風險分佈
- **統計分析圖**: Top 10 高風險設施的坡度 vs 高程散佈圖
- **風險分佈圖**: 各風險等級的數量統計

## AI 診斷日誌

### 🔧 解決的技術問題

#### 1. 「Zonal Stats 回傳 NaN」問題
**症狀**: 部分避難所的地形統計量顯示為 NaN
**根本原因**: 
- CRS 未完全對齊（DEM vs 向量資料）
- 避難所緩衝區超出 DEM 裁切範圍
**解決方案**:
```python
# 1. 確保 CRS 統一
TARGET_CRS = 'EPSG:3826'
dem = dem.rio.reproject(TARGET_CRS)
shelters = shelters.to_crs(TARGET_CRS)

# 2. 擴大裁切範圍（含 1000m 緩衝）
clip_boundary = county_boundary.buffer(1000)
dem_clipped = dem.rio.clip(clip_boundary)

# 3. 添加 NaN 檢查
nan_count = shelters[['mean_elevation', 'max_slope']].isnull().any(axis=1).sum()
if nan_count > 0:
    print(f"⚠️ {nan_count} 個避難所統計為 NaN")
```

#### 2. 「DEM 太大導致 Colab 記憶體不足」問題
**症狀**: 全台 DEM (>500MB) 載入時記憶體溢出
**根本原因**: 未先裁切直接載入完整 DEM
**解決方案**:
```python
# 1. 先裁切後載入（記憶體使用減少 80%+）
clip_boundary = county_boundary_dissolved.buffer(1000)
dem_clipped = dem.rio.clip(clip_boundary.geometry[0])

# 2. 使用預裁切的花蓮縣 DEM
dem_path = 'dem_20m_hualien.tif'  # 已預處理的檔案
dem = rxr.open_rasterio(dem_path)
```

#### 3. 「坡度計算結果不合理」問題
**症狀**: 坡度值過大或過小，不符合實際地形
**根本原因**: `np.gradient` 的 spacing 參數未與 DEM 解析度匹配
**解決方案**:
```python
# 正確的坡度計算（20m 解析度）
dy, dx = np.gradient(dem_values, 20)  # 關鍵：20m spacing
slope = np.degrees(np.arctan(np.sqrt(dx**2 + dy**2)))

# 錯誤寫法：
# dy, dx = np.gradient(dem_values)  # 預設 spacing=1，會導致坡度過大
```

### 🎯 最佳化策略

#### 記憶體管理
- **分階段載入**: 先載入向量資料，再載入裁切後的 DEM
- **即時清理**: 使用 `del` 釋放不需要的大型變數
- **緩衝區優化**: 1000m 緩衝確保邊緣設施的完整分析

#### 效能提升
- **向量化運算**: 使用 NumPy 向量化操作取代迴圈
- **批量處理**: 一次性計算所有避難所的 Zonal Statistics
- **預計算**: Hillshade 和坡度只計算一次，重複使用

## 使用方式

### 1. 環境設定
```bash
# 安裝必要套件
pip install rioxarray rasterstats geopandas python-dotenv matplotlib numpy

# 設定環境變數（編輯 .env 檔案）
cp .env.example .env
```

### 2. 執行分析
```python
# 在 Jupyter Notebook 中依序執行所有 cells
# 或使用 Colab 從 Google Drive 載入 DEM
```

### 3. 輸出結果
- `terrain_risk_audit.json`: 詳細的避難所風險報告
- `terrain_risk_map.png`: 視覺化風險地圖
- `analysis_summary.json`: 分析統計摘要

## 評量標準對應

| 評量項目 | 實作狀況 | 說明 |
|---------|---------|------|
| DEM 載入 + 裁切 + CRS 對齊 | ✅ | 完整實作，含記憶體優化 |
| 坡度計算 + Zonal Statistics | ✅ | 使用 np.gradient + rasterstats |
| 複合風險邏輯（河川距離 + 地形） | ✅ | 四級風險分類系統 |
| 視覺化品質（DEM 地圖 + 統計圖） | ✅ | Hillshade + 風險疊圖 |
| Colab + .env + Markdown + AI 診斷日誌 | ✅ | 完整的專案文檔 |

## 技術規格

- **Python 版本**: 3.8+
- **核心套件**: rioxarray, rasterstats, geopandas, numpy, matplotlib
- **座標系統**: EPSG:3826 (TWD97/TM2)
- **DEM 解析度**: 20m × 20m
- **分析範圍**: 可調整（預設花蓮縣）

## 未來改進方向

1. **即時資料整合**: 接入中央氣象局雨量站資料
2. **機器學習模型**: 使用歷史災害資料訓練風險預測模型
3. **3D 視覺化**: 整合 WebGL 技術提供互動式地形分析
4. **預警系統**: 結合即時監測資料提供動態風險評估

---

**"The professional disaster engineer doesn't just look at location — they measure environmental intensity."**

*ARIA v2.0: From seeing maps to computing risk.*
