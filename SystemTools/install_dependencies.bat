@echo off
REM DPM SystemTools - Dependency Installation Script (Windows)
REM ===========================================================
REM
REM Installs Python dependencies required for SystemTools GUI and log aggregator
REM
REM Usage:
REM   Double-click this file, or run from cmd: install_dependencies.bat
REM

echo ========================================
echo DPM SystemTools - Dependency Installer
echo ========================================
echo.

REM Check Python version
echo [1/4] Checking Python version...

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.8 or higher.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo    Found: Python %PYTHON_VERSION%

REM Simple version check (checks if version starts with "3.")
echo %PYTHON_VERSION% | findstr /r "^3\." >nul
if %errorlevel% neq 0 (
    echo ERROR: Python 3.8+ required (found %PYTHON_VERSION%^)
    pause
    exit /b 1
)

echo    [OK] Python version OK
echo.

REM Check pip
echo [2/4] Checking pip...

python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pip not found. Please reinstall Python with pip.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python -m pip --version') do set PIP_VERSION=%%i
echo    Found: pip %PIP_VERSION%
echo    [OK] pip OK
echo.

REM Check tkinter
echo [3/4] Checking tkinter...

python -c "import tkinter" >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: tkinter not found (required for GUI^)
    echo    Please reinstall Python and check "tcl/tk and IDLE" during installation.
    echo.
    set /p "CONTINUE=Continue anyway? (y/n): "
    if /i not "%CONTINUE%"=="y" (
        exit /b 1
    )
) else (
    echo    [OK] tkinter OK
)
echo.

REM Install dependencies
echo [4/4] Installing Python dependencies from requirements.txt...
echo.

if not exist "requirements.txt" (
    echo ERROR: requirements.txt not found
    echo    Make sure you're running this script from the SystemTools directory
    pause
    exit /b 1
)

echo Installing packages:
echo   - paramiko (SSH client^)
echo   - matplotlib (data visualization^)
echo   - rich (terminal UI^)
echo.

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo [OK] Installation Complete!
echo ========================================
echo.
echo You can now run:
echo   - GUI application:      python main.py
echo   - Log aggregator (CLI): python log_aggregator.py
echo.
echo For help, see: README.md
echo.
pause
