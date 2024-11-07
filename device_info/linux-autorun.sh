#!/bin/bash

# Check if Python is installed
if ! command -v python3 &>/dev/null; then
    echo "Python not found. Installing Python..."
    # Install Python (assumes apt package manager)
    sudo apt update
    sudo apt install -y python3 python3-pip
fi

# Install required Python packages
python3 -m pip install platform socket uuid opencv-python datetime paramiko re psutil getpass

# Run device2.py
python3 device2.py
