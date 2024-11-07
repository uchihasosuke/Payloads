@echo off
REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Installing Python...
    REM Download and install Python silently
    powershell -Command "Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.9.9/python-3.9.9-amd64.exe -OutFile python_installer.exe"
    start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python_installer.exe
)

REM Install required Python packages
pip install platform socket uuid opencv-python datetime paramiko re psutil getpass

REM Run device2.py
python device2.py
exit
