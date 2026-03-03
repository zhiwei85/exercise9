import pandas as pd
import re
import numpy as np

def clean_emergency_shelter_data(input_file, output_file):
    """
    Clean Taiwan emergency shelter data by addressing common data quality issues
    """
    
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    print(f"Original data shape: {df.shape}")
    print("Data quality issues found:")
    
    # 1. Fix missing village names (村里)
    missing_villages = df['村里'].isna().sum()
    print(f"- Missing village names: {missing_villages}")
    
    # 2. Replace question marks with NaN for better handling
    question_mark_cols = ['村里', '管理人姓名', '預計收容村里']
    for col in question_mark_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).replace('?', np.nan)
            df[col] = df[col].astype(str).replace('\?', np.nan, regex=True)
    
    # 3. Fix scientific notation in phone numbers
    def fix_phone_number(phone):
        if pd.isna(phone) or phone == '':
            return phone
        phone_str = str(phone)
        if 'E+' in phone_str:
            try:
                # Convert scientific notation to regular number
                num = float(phone_str)
                return str(int(num))
            except:
                return phone_str
        return phone_str
    
    df['管理人電話'] = df['管理人電話'].apply(fix_phone_number)
    
    # 4. Fix coordinate precision issues
    def fix_coordinate(coord):
        if pd.isna(coord):
            return coord
        try:
            coord_float = float(coord)
            # If coordinate is integer-like, add decimal precision
            if coord_float == int(coord_float):
                return coord_float
            return coord_float
        except:
            return np.nan
    
    df['經度'] = df['經度'].apply(fix_coordinate)
    df['緯度'] = df['緯度'].apply(fix_coordinate)
    
    # 5. Clean address fields
    def clean_address(addr):
        if pd.isna(addr):
            return addr
        addr_str = str(addr)
        # Remove extra whitespace and standardize format
        return ' '.join(addr_str.split())
    
    df['避難收容處所地址'] = df['避難收容處所地址'].apply(clean_address)
    
    # 6. Standardize disaster types
    def clean_disaster_types(disasters):
        if pd.isna(disasters):
            return disasters
        disaster_str = str(disasters)
        # Remove quotes if present and standardize
        disaster_str = disaster_str.replace('"', '')
        # Split by comma and clean each type
        if ',' in disaster_str:
            types = [d.strip() for d in disaster_str.split(',')]
            return ','.join(types)
        return disaster_str.strip()
    
    df['適用災害類別'] = df['適用災害類別'].apply(clean_disaster_types)
    
    # 7. Remove rows with critical missing data
    critical_cols = ['經度', '緯度', '避難收容處所名稱']
    initial_rows = len(df)
    df = df.dropna(subset=critical_cols)
    removed_rows = initial_rows - len(df)
    print(f"- Removed {removed_rows} rows with missing critical data")
    
    # 8. Validate coordinate ranges for Taiwan
    def validate_taiwan_coords(row):
        try:
            lon = float(row['經度'])
            lat = float(row['緯度'])
            # Taiwan coordinates should be approximately:
            # Longitude: 119-123
            # Latitude: 21-26
            if not (119 <= lon <= 123 and 21 <= lat <= 26):
                return False
            return True
        except:
            return False
    
    valid_coords = df.apply(validate_taiwan_coords, axis=1)
    invalid_coords = (~valid_coords).sum()
    print(f"- Found {invalid_coords} rows with invalid Taiwan coordinates")
    
    # Keep only valid coordinates
    df = df[valid_coords]
    
    # 9. Standardize capacity numbers
    def clean_capacity(capacity):
        if pd.isna(capacity):
            return capacity
        try:
            cap_int = int(float(str(capacity)))
            return max(0, cap_int)  # Ensure non-negative
        except:
            return np.nan
    
    df['預計收容人數'] = df['預計收容人數'].apply(clean_capacity)
    
    print(f"Final cleaned data shape: {df.shape}")
    
    # Save cleaned data
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"Cleaned data saved to: {output_file}")
    
    # Generate summary report
    generate_cleaning_report(df, input_file, output_file)
    
    return df

def generate_cleaning_report(df, input_file, output_file):
    """Generate a summary report of the cleaning process"""
    
    report = f"""
# Emergency Shelter Data Cleaning Report

## Input File
- File: {input_file}
- Original Records: {len(pd.read_csv(input_file))}

## Output File  
- File: {output_file}
- Cleaned Records: {len(df)}

## Data Quality Improvements
- Removed records with missing critical data (coordinates, shelter names)
- Fixed scientific notation in phone numbers
- Standardized coordinate formats
- Validated Taiwan coordinate ranges
- Cleaned address formatting
- Standardized disaster type classifications
- Replaced question marks with proper null values

## Data Summary
- Total Shelters: {len(df)}
- Shelters with Village Info: {df['村里'].notna().sum()}
- Shelters with Manager Info: {df['管理人姓名'].notna().sum()}
- Average Capacity: {df['預計收容人數'].mean():.1f} people
- Coordinate Coverage: 100% (all records have valid Taiwan coordinates)

## Remaining Issues
- Some village names still missing (require manual verification)
- Some manager phone numbers may need format standardization
- Disaster type classifications could benefit from further categorization
"""
    
    with open('cleaning_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("Cleaning report saved to: cleaning_report.md")

if __name__ == "__main__":
    input_file = "避難收容處所點位檔案v9 (1).csv"
    output_file = "cleaned_emergency_shelters.csv"
    
    cleaned_data = clean_emergency_shelter_data(input_file, output_file)
