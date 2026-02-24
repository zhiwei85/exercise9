#!/usr/bin/env python3
"""
CWA 氣象 API 使用範例
"""

import os
from dotenv import load_dotenv
from cwa_weather_api import CWAWeatherAPI


def setup_environment():
    """載入環境變數"""
    # 載入 .env 文件
    load_dotenv()
    
    # 檢查 API Key 是否存在
    api_key = os.getenv('CWA_API_KEY')
    if not api_key:
        print("錯誤: 請在 .env 文件中設定 CWA_API_KEY")
        print("範例 .env 文件內容:")
        print("CWA_API_KEY=your_api_key_here")
        return False
    
    print("OK API Key 已成功載入")
    return True


def example_basic_usage():
    """基本使用範例"""
    print("\n=== 基本使用範例 ===")
    
    try:
        cwa_api = CWAWeatherAPI()
        
        # 獲取全台數據
        print("正在獲取全台氣象站數據...")
        df = cwa_api.get_temperature_dataframe()
        
        print(f"成功獲取 {len(df)} 個測站數據")
        
        # 顯示前5個測站
        if not df.empty:
            print("\n前5個測站氣溫數據:")
            display_cols = ['station_name', 'location', 'temperature', 'humidity']
            available_cols = [col for col in display_cols if col in df.columns]
            print(df[available_cols].head().to_string(index=False))
        
    except Exception as e:
        print(f"錯誤: {e}")


def example_specific_cities():
    """特定城市範例"""
    print("\n=== 特定城市氣溫範例 ===")
    
    try:
        cwa_api = CWAWeatherAPI()
        
        # 指定主要城市
        cities = ['台北', '台中', '台南', '高雄', '花蓮']
        print(f"正在獲取 {', '.join(cities)} 的氣溫數據...")
        
        df = cwa_api.get_temperature_dataframe(cities)
        
        if not df.empty:
            print(f"\n成功獲取 {len(df)} 個城市測站數據")
            display_cols = ['location', 'temperature', 'humidity', 'observed_time']
            available_cols = [col for col in display_cols if col in df.columns]
            print(df[available_cols].to_string(index=False))
        else:
            print("未找到指定城市的數據")
            
    except Exception as e:
        print(f"錯誤: {e}")


def example_save_data():
    """保存數據範例"""
    print("\n=== 保存數據範例 ===")
    
    try:
        cwa_api = CWAWeatherAPI()
        
        # 獲取數據並保存
        output_file = cwa_api.save_temperature_data()
        print(f"數據已保存至: {output_file}")
        
    except Exception as e:
        print(f"錯誤: {e}")


def example_temperature_analysis():
    """氣溫分析範例"""
    print("\n=== 氣溫分析範例 ===")
    
    try:
        cwa_api = CWAWeatherAPI()
        
        # 獲取全台數據
        df = cwa_api.get_temperature_dataframe()
        
        if df.empty or 'temperature' not in df.columns:
            print("無法獲取氣溫數據")
            return
        
        # 氣溫統計
        temp_stats = df['temperature'].describe()
        print(f"氣溫統計分析:")
        print(f"測站數量: {len(df)}")
        print(f"平均氣溫: {temp_stats['mean']:.1f}°C")
        print(f"最高氣溫: {temp_stats['max']:.1f}°C")
        print(f"最低氣溫: {temp_stats['min']:.1f}°C")
        print(f"標準差: {temp_stats['std']:.1f}°C")
        
        # 找出最熱和最冷的測站
        hottest = df.loc[df['temperature'].idxmax()]
        coldest = df.loc[df['temperature'].idxmin()]
        
        print(f"\n最熱測站: {hottest['station_name']} ({hottest['location']}) - {hottest['temperature']:.1f}°C")
        print(f"最冷測站: {coldest['station_name']} ({coldest['location']}) - {coldest['temperature']:.1f}°C")
        
        # 氣溫分佈
        temp_ranges = [
            ("低於 20°C", df[df['temperature'] < 20]),
            ("20-25°C", df[(df['temperature'] >= 20) & (df['temperature'] < 25)]),
            ("25-30°C", df[(df['temperature'] >= 25) & (df['temperature'] < 30)]),
            ("30°C 以上", df[df['temperature'] >= 30])
        ]
        
        print(f"\n氣溫分佈:")
        for range_name, stations in temp_ranges:
            count = len(stations)
            percentage = (count / len(df)) * 100
            print(f"{range_name}: {count} 個測站 ({percentage:.1f}%)")
        
    except Exception as e:
        print(f"錯誤: {e}")


def main():
    """主函數"""
    print("CWA 氣象 API 使用範例")
    print("=" * 50)
    
    # 設定環境
    if not setup_environment():
        return
    
    # 執行各種範例
    example_basic_usage()
    example_specific_cities()
    example_save_data()
    example_temperature_analysis()
    
    print("\n" + "=" * 50)
    print("範例執行完成!")


if __name__ == "__main__":
    main()
