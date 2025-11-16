@echo off
echo Building Modbus Tester executable...
echo.

REM Check if PyInstaller is installed
python -m pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
)

REM Build the executable
python build_exe.py

if errorlevel 1 (
    echo.
    echo Build failed. Check the output above for errors.
    pause
    exit /b 1
)

echo.
echo Build complete! Executable is in the 'dist' folder.
echo.
pause
