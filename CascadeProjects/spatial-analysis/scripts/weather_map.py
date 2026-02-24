#!/usr/bin/env python3
"""
使用 Folium 在地圖上標示 CWA 測站位置
依據氣溫進行分色顯示
"""

import os
import pandas as pd
import folium
from folium.plugins import HeatMap
import numpy as np
from typing import Optional, List
import branca.colormap as cm

# 設定API金鑰
os.environ['CWA_API_KEY'] = "CWA-6310DF17-9FBC-4F67-B67B-F70BDEE7F379"

from cwa_weather_api import CWAWeatherAPI


class WeatherMapVisualizer:
    def __init__(self):
        """初始化地圖視覺化工具"""
        self.cwa_api = CWAWeatherAPI()
        
    def get_temperature_color(self, temp: Optional[float]) -> str:
        """
        根據氣溫返回顏色
        
        Args:
            temp: 氣溫值
            
        Returns:
            顏色代碼
        """
        if temp is None or pd.isna(temp):
            return '#808080'  # 灰色 - 無數據
        
        if temp < 20:
            return '#0000FF'  # 藍色 - 低溫
        elif 20 <= temp <= 28:
            return '#00FF00'  # 綠色 - 適中
        else:
            return '#FFA500'  # 橘色 - 高溫
    
    def create_weather_map(self, location_names: Optional[List[str]] = None, 
                       center: List[float] = [23.8, 120.9], zoom: int = 7) -> folium.Map:
        """
        創建氣象地圖
        
        Args:
            location_names: 可選的地點名稱列表
            center: 地圖中心座標 [緯度, 經度]
            zoom: 縮放級別
            
        Returns:
            Folium 地圖物件
        """
        # 獲取氣象數據
        print("正在獲取氣象數據...")
        df = self.cwa_api.get_temperature_dataframe(location_names)
        
        if df.empty:
            raise ValueError("無法獲取氣象數據")
        
        # 過濾有效座標的測站
        valid_df = df[(df['latitude'] != 0) & (df['longitude'] != 0)].copy()
        
        if valid_df.empty:
            raise ValueError("沒有有效的測站座標數據")
        
        print(f"找到 {len(valid_df)} 個有效測站")
        
        # 計算地圖中心（如果沒有指定）
        if center == [23.8, 120.9]:
            center_lat = valid_df['latitude'].mean()
            center_lon = valid_df['longitude'].mean()
            center = [center_lat, center_lon]
        
        # 創建地圖
        m = folium.Map(
            location=center,
            zoom_start=zoom,
            tiles='OpenStreetMap'
        )
        
        # 創建氣溫色階圖例
        colormap = cm.LinearColormap(
            colors=['#0000FF', '#00FF00', '#FFA500'],
            vmin=15,
            vmax=35,
            caption='氣溫 (°C)'
        )
        colormap.add_to(m)
        
        # 添加測站標記
        for idx, row in valid_df.iterrows():
            temp = row.get('temperature')
            color = self.get_temperature_color(temp)
            
            # 創建彈出視窗內容
            temp_display = f"{temp:.1f}°C" if temp is not None else 'N/A'
            popup_content = f"""
            <b>{row.get('station_name', '未知測站')}</b><br>
            測站ID: {row.get('station_id', 'N/A')}<br>
            位置: {row.get('location', 'N/A')}<br>
            座標: {row.get('latitude', 0):.4f}, {row.get('longitude', 0):.4f}<br>
            氣溫: {temp_display}<br>
            濕度: {row.get('humidity', 'N/A')}%<br>
            天氣: {row.get('weather', 'N/A')}<br>
            觀測時間: {row.get('observed_time', 'N/A')}
            """
            
            # 創建圓形標記
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=8,
                popup=folium.Popup(popup_content, max_width=300),
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.7,
                weight=2,
                tooltip=f"{row.get('station_name', '未知')}: {temp:.1f}°C" if temp is not None else f"{row.get('station_name', '未知')}: 無數據"
            ).add_to(m)
            
            # 添加測站名稱標籤
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                icon=folium.DivIcon(
                    html=f'<div style="font-size: 10px; color: black; font-weight: bold;">{row.get("station_name", "")}</div>',
                    icon_size=(60, 20),
                    icon_anchor=(30, -10)
                )
            ).add_to(m)
        
        # 添加統計信息
        stats_html = self._create_stats_html(valid_df)
        m.get_root().html.add_child(folium.Element(stats_html))
        
        return m
    
    def _create_stats_html(self, df: pd.DataFrame) -> str:
        """創建統計信息HTML"""
        total_stations = len(df)
        temp_data = df['temperature'].dropna()
        
        if not temp_data.empty:
            avg_temp = temp_data.mean()
            max_temp = temp_data.max()
            min_temp = temp_data.min()
            
            # 按溫度分組統計
            cold_stations = len(temp_data[temp_data < 20])
            normal_stations = len(temp_data[(temp_data >= 20) & (temp_data <= 28)])
            hot_stations = len(temp_data[temp_data > 28])
        else:
            avg_temp = max_temp = min_temp = 0
            cold_stations = normal_stations = hot_stations = 0
        
        html = f"""
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 250px; height: 140px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <h4>氣象統計</h4>
        <p>總測站數: {total_stations}</p>
        <p>平均氣溫: {avg_temp:.1f}°C</p>
        <p>最高氣溫: {max_temp:.1f}°C</p>
        <p>最低氣溫: {min_temp:.1f}°C</p>
        <p><span style="color: blue;">● 低溫(&lt;20°C): {cold_stations}</span></p>
        <p><span style="color: green;">● 適中(20-28°C): {normal_stations}</span></p>
        <p><span style="color: orange;">● 高溫(&gt;28°C): {hot_stations}</span></p>
        </div>
        """
        return html
    
    def create_heatmap(self, location_names: Optional[List[str]] = None) -> folium.Map:
        """
        創建氣溫熱力圖
        
        Args:
            location_names: 可選的地點名稱列表
            
        Returns:
            Folium 地圖物件
        """
        # 獲取氣象數據
        df = self.cwa_api.get_temperature_dataframe(location_names)
        
        # 過濾有效數據
        valid_df = df[(df['latitude'] != 0) & (df['longitude'] != 0) & 
                     df['temperature'].notna()].copy()
        
        if valid_df.empty:
            raise ValueError("沒有有效的氣溫數據")
        
        # 計算地圖中心
        center_lat = valid_df['latitude'].mean()
        center_lon = valid_df['longitude'].mean()
        
        # 創建地圖
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=7,
            tiles='OpenStreetMap'
        )
        
        # 準備熱力圖數據
        heat_data = []
        for idx, row in valid_df.iterrows():
            heat_data.append([row['latitude'], row['longitude'], row['temperature']])
        
        # 添加熱力圖
        HeatMap(
            heat_data,
            min_opacity=0.4,
            radius=25,
            blur=15,
            gradient={
                0.0: 'blue',
                0.3: 'cyan',
                0.5: 'lime',
                0.7: 'yellow',
                1.0: 'red'
            }
        ).add_to(m)
        
        return m
    
    def save_map(self, map_obj: folium.Map, filename: str = "weather_map.html") -> str:
        """
        保存地圖到HTML文件
        
        Args:
            map_obj: Folium地圖物件
            filename: 輸出文件名
            
        Returns:
            保存的文件路徑
        """
        output_path = f"../outputs/{filename}"
        map_obj.save(output_path)
        print(f"地圖已保存至: {output_path}")
        return output_path


def main():
    """主函數"""
    try:
        # 初始化視覺化工具
        visualizer = WeatherMapVisualizer()
        
        print("=== CWA 氣象地圖視覺化 ===")
        
        # 創建完整地圖
        print("\n1. 創建測站分布地圖...")
        weather_map = visualizer.create_weather_map()
        
        # 保存地圖
        map_file = visualizer.save_map(weather_map, "taiwan_weather_stations.html")
        
        # 創建主要城市地圖
        print("\n2. 創建主要城市地圖...")
        major_cities = ['台北', '新北', '桃園', '台中', '台南', '高雄', '宜蘭', '花蓮']
        cities_map = visualizer.create_weather_map(
            location_names=major_cities,
            center=[23.8, 120.9],
            zoom=8
        )
        cities_file = visualizer.save_map(cities_map, "major_cities_weather.html")
        
        # 創建熱力圖
        print("\n3. 創建氣溫熱力圖...")
        try:
            heatmap = visualizer.create_heatmap()
            heatmap_file = visualizer.save_map(heatmap, "temperature_heatmap.html")
        except Exception as e:
            print(f"熱力圖創建失敗: {e}")
        
        print(f"\n=== 完成 ===")
        print(f"測站地圖: {map_file}")
        print(f"城市地圖: {cities_file}")
        if 'heatmap_file' in locals():
            print(f"熱力圖: {heatmap_file}")
        
        print(f"\n請在瀏覽器中打開HTML文件查看地圖")
        
    except Exception as e:
        print(f"執行錯誤: {e}")


if __name__ == "__main__":
    main()
