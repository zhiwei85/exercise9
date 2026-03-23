@echo off
echo ========================================
echo Complete Environment Reset for ARIA v2.0
echo ========================================
echo.

echo Step 1: Deactivate current conda environment (if active)
call conda deactivate 2>nul

echo Step 2: Create new clean environment
conda create -n aria_v2 python=3.11 -y
call conda activate aria_v2

echo Step 3: Install compatible packages
echo Installing NumPy 1.26.4 (compatible with all GIS packages)...
pip install "numpy==1.26.4"

echo Installing pandas and scipy...
pip install "pandas==2.2.2" "scipy==1.13.1"

echo Installing matplotlib (compatible version)...
pip install "matplotlib==3.8.4"

echo Installing GIS packages...
pip install "geopandas==1.0.1" "rasterstats==0.20.0" "rioxarray==0.19.0"
pip install "shapely==2.0.4" "fiona==1.9.5" "pyproj==3.7.0"

echo Installing additional packages...
pip install python-dotenv jupyter

echo.
echo ========================================
echo Environment reset completed!
echo ========================================
echo.
echo IMPORTANT: Please restart your terminal and run:
echo conda activate aria_v2
echo jupyter notebook
echo.
echo Then open ARIA_v2.ipynb in the new environment
pause
