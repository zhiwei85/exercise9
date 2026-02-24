#!/usr/bin/env python3
"""
檢查CWA API回應的詳細結構，尋找氣溫數據
"""

import os
import requests
import json

# 設定API金鑰
os.environ['CWA_API_KEY'] = "CWA-6310DF17-9FBC-4F67-B67B-F70BDEE7F379"

def check_api_structure():
    """檢查API回應結構"""
    url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001"
    params = {
        'Authorization': os.getenv('CWA_API_KEY'),
        'format': 'JSON'
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if 'records' in data and 'Station' in data['records']:
            stations = data['records']['Station']
            
            # 檢查前3個測站的完整結構
            for i, station in enumerate(stations[:3]):
                print(f"\n=== 測站 {i+1}: {station.get('StationName', 'N/A')} ===")
                
                # 檢查所有可能的氣溫相關欄位
                for key, value in station.items():
                    if any(keyword in key.lower() for keyword in ['temp', 'temperature', 'air', '氣溫', '溫度']):
                        print(f"{key}: {value}")
                
                # 檢查WeatherElement詳細內容
                if 'WeatherElement' in station:
                    weather_elements = station['WeatherElement']
                    print(f"WeatherElement類型: {type(weather_elements)}")
                    print(f"WeatherElement內容: {weather_elements}")
                    
                    # 如果是列表，顯示每個元素
                    if isinstance(weather_elements, list):
                        for j, element in enumerate(weather_elements):
                            print(f"  Element {j}: {element}")
                
                print("-" * 50)
        
        # 檢查API文檔中的fields
        if 'result' in data and 'fields' in data['result']:
            fields = data['result']['fields']
            print(f"\n=== API Fields ===")
            for field in fields:
                field_id = field.get('id', '')
                if any(keyword in field_id.lower() for keyword in ['temp', 'air']):
                    print(f"Field: {field}")
        
    except Exception as e:
        print(f"錯誤: {e}")

def check_other_endpoints():
    """檢查其他可能的API端點"""
    # 常見的CWA氣象觀測端點
    endpoints = [
        "O-A0001-001",  # 自動氣象站-即時觀測
        "O-A0002-001",  # 自動雨量站-即時觀測
        "O-A0003-001",  # 自動氣象站-觀測資料
        "F-C0032-001",  # 36小時天氣預報
    ]
    
    base_url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore"
    
    for endpoint in endpoints:
        print(f"\n=== 檢查端點: {endpoint} ===")
        url = f"{base_url}/{endpoint}"
        params = {
            'Authorization': os.getenv('CWA_API_KEY'),
            'format': 'JSON',
            'limit': 1  # 只獲取一筆資料檢查結構
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✓ 端點可用")
                
                # 檢查是否有氣溫相關欄位
                if 'records' in data:
                    records = data['records']
                    if isinstance(records, dict) and 'Station' in records:
                        station = records['Station'][0] if records['Station'] else {}
                        print(f"  測站範例: {station.get('StationName', 'N/A')}")
                        
                        # 檢查欄位
                        for key in station.keys():
                            if any(keyword in key.lower() for keyword in ['temp', 'air']):
                                print(f"  找到氣溫欄位: {key}")
            else:
                print(f"✗ 端點不可用 (HTTP {response.status_code})")
                
        except Exception as e:
            print(f"✗ 端點錯誤: {e}")

if __name__ == "__main__":
    print("=== 檢查CWA API氣溫數據 ===")
    check_api_structure()
    check_other_endpoints()
