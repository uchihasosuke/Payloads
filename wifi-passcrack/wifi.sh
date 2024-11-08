#!/bin/bash

# Script to download and run wifi6.py with sudo

# Check if wifi6.py exists locally
if [ -f "wifi6.py" ]; then
    echo "Running existing wifi6.py..."
    sudo python3 wifi6.py
else
    echo "Downloading wifi6.py from GitHub..."
    git clone https://github.com/yourusername/wifi6.git
    cd wifi6
    sudo python3 wifi6.py
fi

