#!/usr/bin/env python3
import os
import requests
import json

# 設定API金鑰
os.environ['CWA_API_KEY'] = "CWA-6310DF17-9FBC-4F67-B67B-F70BDEE7F379"

# 測試API
url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001"
params = {
    'Authorization': os.getenv('CWA_API_KEY'),
    'format': 'JSON'
}

try:
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    
    print("API回應結構:")
    print(json.dumps(data, indent=2, ensure_ascii=False)[:1000] + "...")
    
    print(f"\nrecords keys: {list(data.get('records', {}).keys())}")
    
    if 'records' in data and 'Station' in data['records']:
        stations = data['records']['Station']
        print(f"測站數量: {len(stations)}")
        if stations:
            first_station = stations[0]
            print(f"第一個測站keys: {list(first_station.keys())}")
            
            # 檢查WeatherElement結構
            if 'WeatherElement' in first_station:
                weather_elements = first_station['WeatherElement']
                print(f"WeatherElement數量: {len(weather_elements)}")
                if weather_elements:
                    for i, element in enumerate(weather_elements):
                        if i >= 3:  # 只顯示前3個
                            break
                        print(f"WeatherElement {i}: {element}")
            
            # 檢查時間格式
            obs_time = first_station.get('ObsTime', '')
            print(f"觀測時間: '{obs_time}'")
    
except Exception as e:
    print(f"錯誤: {e}")
