# NumPy 版本相容性問題解決方案

## 問題描述
執行 ARIA v2.0 時遇到以下錯誤：
```
A module that was compiled using NumPy 1.x cannot be run in NumPy 2.4.3 as it may crash
```

## 根本原因
- 某些地理空間分析套件（如 `rasterstats`, `geopandas`）是使用 NumPy 1.x 編譯的
- 當前環境安裝了 NumPy 2.4.3，導致版本不相容

## 解決方案

### 方法 1：降級 NumPy（推薦）
```bash
# 強制重新安裝相容版本
pip install "numpy<2.0.0" --force-reinstall --no-cache-dir

# 重新安裝其他相依套件
pip install rioxarray rasterstats geopandas python-dotenv matplotlib pandas scipy shapely fiona pyproj
```

### 方法 2：使用 requirements.txt
```bash
# 使用更新後的 requirements.txt
pip install -r requirements.txt --force-reinstall --no-cache-dir
```

### 方法 3：建立新的虛擬環境
```bash
# 建立新的乾淨環境
python -m venv aria_env
source aria_env/bin/activate  # Linux/Mac
# 或 aria_env\Scripts\activate  # Windows

# 安裝相容版本
pip install "numpy<2.0.0"
pip install -r requirements.txt
```

## 驗證安裝
```python
import numpy as np
print(f"NumPy version: {np.__version__}")

# 測試地理空間套件
import geopandas as gpd
import rasterstats
import rioxarray as rxr
print("✅ All packages imported successfully")
```

## 預期結果
- NumPy 版本應為 1.x.x（如 1.26.4）
- 所有地理空間套件應能正常載入
- ARIA v2.0 notebook 應能正常執行

## 注意事項
- NumPy 2.0 引入了許多破壞性變更
- 建議在專業 GIS 分析環境中暫時使用 NumPy 1.x
- 未來套件更新後可考慮升級至 NumPy 2.x

## 技術細節
- **錯誤類型**: ABI (Application Binary Interface) 不相容
- **影響套件**: 主要影響編譯擴展的套件
- **解決原理**: 確保所有套件使用相同的 NumPy ABI 版本
