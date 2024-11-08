#!/bin/bash

# Script to download and run wifi-passcrack.py with sudo

# Check if wifi-pass.py exists locally
if [ -f "wifi-passcrack.py" ]; then
    echo "Running existing wifi-passcrack.py..."
    sudo python3 wifi-passcrack.py
else
    echo "Downloading wifi-passcrack.pyfrom GitHub..."
    git clone https://github.com/uchihasosuke/Payloads.git
    cd Payloads/wifi-passcrack
    sudo python3 wifi-passcrack.py
fi