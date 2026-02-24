#!/usr/bin/env python3
"""
中央氣象署(CWA)自動氣象站觀測數據獲取腳本
API: O-A0003-001 (自動氣象站-觀測資料)
"""

import os
import requests
import json
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd


class CWAWeatherAPI:
    def __init__(self):
        """初始化 CWA API 客戶端"""
        self.api_key = self._load_api_key()
        self.base_url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore"
        self.dataset_id = "O-A0003-001"
        
    def _load_api_key(self) -> str:
        """從環境變數讀取 CWA API Key"""
        api_key = os.getenv('CWA_API_KEY')
        if not api_key:
            # 如果環境變數不存在，使用預設金鑰
            api_key = "CWA-6310DF17-9FBC-4F67-B67B-F70BDEE7F379"
            print(f"使用預設 API Key")
        return api_key
    
    def fetch_weather_data(self, location_names: Optional[List[str]] = None) -> Dict:
        """
        獲取自動氣象站觀測數據
        
        Args:
            location_names: 可選的地點名稱列表，如 ['台北', '高雄', '台中']
        
        Returns:
            API 回應的 JSON 數據
        """
        url = f"{self.base_url}/{self.dataset_id}"
        params = {
            'Authorization': self.api_key,
            'format': 'JSON'
        }
        
        # 如果指定了地點，添加 LocationName 參數
        if location_names:
            params['LocationName'] = ','.join(location_names)
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API 請求失敗: {e}")
    
    def extract_temperature_data(self, weather_data: Dict) -> List[Dict]:
        """
        從 API 回應中提取氣溫數據
        
        Args:
            weather_data: API 回應的 JSON 數據
        
        Returns:
            包含氣溫資訊的字典列表
        """
        temperature_records = []
        
        if 'records' not in weather_data or 'Station' not in weather_data['records']:
            raise ValueError("無效的 API 回應格式")
        
        stations = weather_data['records']['Station']
        
        for station in stations:
            try:
                station_info = {
                    'station_id': station.get('StationId', ''),
                    'station_name': station.get('StationName', ''),
                    'location': station.get('StationName', ''),  # CWA API使用StationName作為地點名稱
                    'latitude': float(station.get('GeoInfo', {}).get('Coordinates', [{}])[0].get('StationLatitude', 0)),
                    'longitude': float(station.get('GeoInfo', {}).get('Coordinates', [{}])[0].get('StationLongitude', 0)),
                    'temperature': None,
                    'humidity': None,
                    'weather': None
                }
                
                # 處理觀測時間
                obs_time = station.get('ObsTime', '')
                if isinstance(obs_time, str) and obs_time.startswith('{'):
                    # 解析JSON格式的時間
                    try:
                        time_data = json.loads(obs_time)
                        station_info['observed_time'] = time_data.get('DateTime', '')
                    except:
                        station_info['observed_time'] = obs_time
                else:
                    station_info['observed_time'] = obs_time
                
                # 提取氣象要素 - WeatherElement是字典格式
                weather_elements = station.get('WeatherElement', {})
                if isinstance(weather_elements, dict):
                    # 提取氣溫
                    if 'AirTemperature' in weather_elements:
                        try:
                            station_info['temperature'] = float(weather_elements['AirTemperature'])
                        except (ValueError, TypeError):
                            station_info['temperature'] = None
                    
                    # 提取濕度
                    if 'RelativeHumidity' in weather_elements:
                        try:
                            station_info['humidity'] = float(weather_elements['RelativeHumidity'])
                        except (ValueError, TypeError):
                            station_info['humidity'] = None
                    
                    # 提取天氣狀況
                    if 'Weather' in weather_elements:
                        station_info['weather'] = weather_elements['Weather']
                    
                    # 提取氣壓
                    if 'AirPressure' in weather_elements:
                        station_info['pressure'] = weather_elements['AirPressure']
                    
                    # 提取風速
                    if 'WindSpeed' in weather_elements:
                        station_info['wind_speed'] = weather_elements['WindSpeed']
                    
                    # 提取UV指數
                    if 'UVIndex' in weather_elements:
                        station_info['uv_index'] = weather_elements['UVIndex']
                
                temperature_records.append(station_info)
                
            except (ValueError, KeyError, TypeError) as e:
                print(f"處理測站數據時發生錯誤: {e}")
                continue
        
        return temperature_records
    
    def get_temperature_dataframe(self, location_names: Optional[List[str]] = None) -> pd.DataFrame:
        """
        獲取氣溫數據並轉換為 pandas DataFrame
        
        Args:
            location_names: 可選的地點名稱列表
        
        Returns:
            包含氣溫數據的 DataFrame
        """
        weather_data = self.fetch_weather_data(location_names)
        temperature_records = self.extract_temperature_data(weather_data)
        
        df = pd.DataFrame(temperature_records)
        
        # 轉換時間格式
        if 'observed_time' in df.columns:
            df['observed_time'] = pd.to_datetime(df['observed_time'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        
        # 按氣溫排序
        if 'temperature' in df.columns:
            df = df.sort_values('temperature', ascending=False)
        
        return df
    
    def save_temperature_data(self, location_names: Optional[List[str]] = None, 
                            output_dir: str = "../outputs") -> str:
        """
        獲取氣溫數據並保存為 CSV 文件
        
        Args:
            location_names: 可選的地點名稱列表
            output_dir: 輸出目錄路徑
        
        Returns:
            保存的文件路徑
        """
        df = self.get_temperature_dataframe(location_names)
        
        # 確保輸出目錄存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cwa_temperature_data_{timestamp}.csv"
        filepath = os.path.join(output_dir, filename)
        
        # 保存數據
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"氣溫數據已保存至: {filepath}")
        
        return filepath


def main():
    """主函數 - 示範如何使用 CWA API"""
    try:
        # 初始化 API 客戶端
        cwa_api = CWAWeatherAPI()
        
        # 獲取全台氣象站數據
        print("正在獲取全台自動氣象站數據...")
        df = cwa_api.get_temperature_dataframe()
        
        # 顯示基本統計信息
        print(f"\n成功獲取 {len(df)} 個測站數據")
        print(f"數據時間範圍: {df['observed_time'].min()} ~ {df['observed_time'].max()}")
        
        # 顯示氣溫統計
        if 'temperature' in df.columns and df['temperature'].notna().any():
            temp_stats = df['temperature'].describe()
            print(f"\n氣溫統計:")
            print(f"平均氣溫: {temp_stats['mean']:.1f}°C")
            print(f"最高氣溫: {temp_stats['max']:.1f}°C")
            print(f"最低氣溫: {temp_stats['min']:.1f}°C")
        else:
            print("\n注意: 目前API端點未提供氣溫數據，僅提供基本測站資訊")
        
        # 顯示前10個測站的氣溫數據
        print("\n前10個測站氣溫數據:")
        display_columns = ['station_name', 'location', 'temperature', 'humidity', 'observed_time']
        available_columns = [col for col in display_columns if col in df.columns]
        print(df[available_columns].head(10).to_string(index=False))
        
        # 保存數據
        output_file = cwa_api.save_temperature_data()
        
        # 示範獲取特定城市數據
        print("\n正在獲取主要城市氣溫數據...")
        major_cities = ['台北', '新北', '桃園', '台中', '台南', '高雄', '宜蘭', '花蓮']
        cities_df = cwa_api.get_temperature_dataframe(major_cities)
        
        if not cities_df.empty:
            print("\n主要城市氣溫:")
            city_columns = ['location', 'temperature', 'humidity', 'observed_time']
            available_city_columns = [col for col in city_columns if col in cities_df.columns]
            print(cities_df[available_city_columns].to_string(index=False))
        
    except Exception as e:
        print(f"執行錯誤: {e}")


if __name__ == "__main__":
    main()
