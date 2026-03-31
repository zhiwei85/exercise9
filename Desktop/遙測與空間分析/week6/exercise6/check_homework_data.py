import json

# Check the homework5 data file
with open(r'c:\Users\user\Desktop\遙測與空間分析\week5\homework5\data\fungwong_202511.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('Structure of homework5 data file:')
if 'records' in data:
    print('Has records field')
    station = data['records']['Station'][0]
    print('First station GeoInfo:')
    print(json.dumps(station['GeoInfo'], indent=2, ensure_ascii=False))
else:
    print('Different structure - showing top level keys:')
    for key in data.keys():
        print(f'  {key}')
