@echo off
echo Fixing NumPy compatibility issue for Windows...
echo.

echo Step 1: Uninstalling conflicting packages...
pip uninstall numpy pandas geopandas rasterstats rioxarray scipy -y

echo Step 2: Installing compatible NumPy version...
pip install "numpy==1.26.4"

echo Step 3: Installing compatible versions of other packages...
pip install "pandas==2.2.2" "scipy==1.13.1"
pip install "geopandas==1.0.1" "rasterstats==0.20.0" "rioxarray==0.19.0"
pip install python-dotenv matplotlib shapely fiona pyproj

echo.
echo ✅ NumPy compatibility fix completed
echo Please restart your Jupyter kernel and try again
pause
