import json

with open(r'c:\Users\user\Desktop\遙測與空間分析\week5\exercise5\data\scenarios\fungwong_202511.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

station = data['records']['Station'][0]
print('Complete structure of first station:')
print(json.dumps(station, indent=2, ensure_ascii=False))

# Check for any coordinate fields
print('\nLooking for coordinate fields...')
for key in station.keys():
    if 'lat' in key.lower() or 'lon' in key.lower() or 'coord' in key.lower():
        print(f'Found coordinate field: {key}')

# Check GeoInfo structure
print('\nGeoInfo structure:')
print(json.dumps(station['GeoInfo'], indent=2, ensure_ascii=False))
