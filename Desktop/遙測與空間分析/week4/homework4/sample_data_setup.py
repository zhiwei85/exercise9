#!/usr/bin/env python3
"""
創建 ARIA v2.0 示例資料
避免網路下載問題，使用本地示例資料進行分析
"""

import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon, Point
import numpy as np

def create_sample_data():
    """創建示例資料檔案"""
    
    # 1. 創建示例河川資料
    rivers_data = [
        {
            'geometry': Polygon([(121.5, 23.8), (121.7, 23.8), (121.7, 24.0), (121.5, 24.0), (121.5, 23.8)]),
            'name': '花蓮溪',
            'RIVER_NAME': '花蓮溪'
        },
        {
            'geometry': Polygon([(121.6, 23.9), (121.8, 23.9), (121.8, 24.1), (121.6, 24.1), (121.6, 23.9)]),
            'name': '秀姑巒溪',
            'RIVER_NAME': '秀姑巒溪'
        }
    ]
    
    rivers_gdf = gpd.GeoDataFrame(rivers_data, crs='EPSG:4326')
    rivers_gdf.to_crs('EPSG:3826', inplace=True)
    rivers_gdf.to_file('rivers.shp', encoding='utf-8')
    print("✅ Created rivers.shp")
    
    # 2. 創建示例避難所資料
    shelters_data = [
        {'name': '花蓮市避難所1', 'longitude': 121.607, 'latitude': 23.981, 'address': '花蓮市中正路123號'},
        {'name': '花蓮市避難所2', 'longitude': 121.623, 'latitude': 23.975, 'address': '花蓮市中山路456號'},
        {'name': '吉安鄉避難所1', 'longitude': 121.545, 'latitude': 23.961, 'address': '吉安鄉建國路78號'},
        {'name': '吉安鄉避難所2', 'longitude': 121.558, 'latitude': 23.958, 'address': '吉安鄉中正路234號'},
        {'name': '壽豐鄉避難所1', 'longitude': 121.508, 'latitude': 23.849, 'address': '壽豐鄉中山路567號'},
        {'name': '壽豐鄉避難所2', 'longitude': 121.521, 'latitude': 23.842, 'address': '壽豐鄉中正路890號'},
        {'name': '新城鄉避難所1', 'longitude': 121.640, 'latitude': 24.018, 'address': '新城鄉中正路345號'},
        {'name': '新城鄉避難所2', 'longitude': 121.653, 'latitude': 24.011, 'address': '新城鄉中山路678號'},
        {'name': '玉里鎮避難所1', 'longitude': 121.317, 'latitude': 23.338, 'address': '玉里鎮中正路901號'},
        {'name': '玉里鎮避難所2', 'longitude': 121.330, 'latitude': 23.331, 'address': '玉里鎮中山路234號'},
        {'name': '瑞穗鄉避難所1', 'longitude': 121.357, 'latitude': 23.366, 'address': '瑞穗鄉中正路567號'}
    ]
    
    shelters_df = pd.DataFrame(shelters_data)
    shelters_df.to_csv('emergency_shelters.csv', index=False, encoding='utf-8-sig')
    print("✅ Created emergency_shelters.csv")
    
    # 3. 創建示例鄉鎮界資料
    townships_data = [
        {
            'geometry': Polygon([(121.3, 23.3), (121.8, 23.3), (121.8, 24.2), (121.3, 24.2), (121.3, 23.3)]),
            'COUNTY_NAME': '花蓮縣',
            'TOWN_NAME': '花蓮縣',
            'COUNTYCODE': '10002',
            'TOWNCODE': '10002010'
        }
    ]
    
    townships_gdf = gpd.GeoDataFrame(townships_data, crs='EPSG:4326')
    townships_gdf.to_crs('EPSG:3826', inplace=True)
    townships_gdf.to_file('township_boundaries.shp', encoding='utf-8')
    print("✅ Created township_boundaries.shp")
    
    # 4. 創建示例 DEM 檔案（如果需要）
    try:
        import rioxarray as rxr
        # 創建一個小的示例 DEM（20m 解析度）
        x = np.linspace(121.3, 121.8, 100)
        y = np.linspace(23.3, 24.2, 100)
        X, Y = np.meshgrid(x, y)
        
        # 創建真實地形（花蓮縣地形特徵）
        Z = 50 + 200 * np.exp(-((X-121.6)**2/0.01 - (Y-23.9)**2/0.01) + \
            100 * np.exp(-((X-121.5)**2/0.02 - (Y-23.8)**2/0.02)
        
        # 轉換為 xarray 並設定 CRS
        import xarray as xr
        da = xr.DataArray(
            Z,
            coords={'y': y, 'x': x},
            dims=['y', 'x']
        )
        da.rio.write_crs('EPSG:3826', inplace=True)
        da.rio.write_transform(da.rio.transform(), inplace=True)
        
        # 儲存為 GeoTIFF
        da.rio.to_raster('dem_20m_hualien.tif')
        print('✅ Created dem_20m_hualien.tif')
        
    except Exception as e:
        print(f'⚠️ Could not create sample DEM: {e}')
        print('Please use your own DEM file')
    
    print("\n🎉 All sample data files created!")
    print("Files created:")
    print("- rivers.shp")
    print("- emergency_shelters.csv") 
    print("- township_boundaries.shp")
    print("- dem_20m_hualien.tif (if successful)")

if __name__ == "__main__":
    create_sample_data()
