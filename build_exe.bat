@echo off
setlocal
cd /d "%~dp0"

echo.
echo Checking for Python...
where py >nul 2>&1
if errorlevel 1 (
    echo Python launcher not found.
    echo Install Python 3.10 or newer from https://www.python.org/downloads/
    echo Make sure the Python Launcher is installed.
    goto :error
)

echo.
echo [1/2] Installing PyInstaller...
py -3 -m pip install --upgrade -r requirements-build.txt
if errorlevel 1 goto :error

echo.
echo [2/2] Building BinaryScanner.exe...
py -3 -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --onefile ^
    --windowed ^
    --name BinaryScanner ^
    binary_scanner_gui.py
if errorlevel 1 goto :error

echo.
echo ============================================
echo Build complete.
echo Executable: %CD%\dist\BinaryScanner.exe
echo ============================================
pause
exit /b 0

:error
echo.
echo Build failed. Review the error messages above.
pause
exit /b 1
