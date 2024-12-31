import os
import json
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from colorama import Fore, init
import pyfiglet
import sys
from tqdm import tqdm

# Initialize colorama for color output
init(autoreset=True)

# Function to clear the terminal screen
def clear_terminal():
    """Clears the terminal screen depending on the OS."""
    if os.name == 'nt':  # For Windows
        os.system('cls')
    else:  # For Linux/Mac
        os.system('clear')

# Function to print a stylish banner with ASCII art for "Saavn Downloader"
def print_advanced_banner():
    """Prints a customized banner for Saavn Downloader."""
    logo = '''
     8              8""""8                                       
    8  e  eeeee    8      eeeee eeeee ee   e eeeee              
    8e 8  8  88    8eeeee 8   8 8   8 88   8 8   8              
    88 8e 8   8        88 8eee8 8eee8 88  e8 8e  8              
e   88 88 8   8    e   88 88  8 88  8  8  8  88  8              
8eee88 88 8eee8    8eee88 88  8 88  8  8ee8  88  8              
                                                                
8""""8                                                          
8    8 eeeee e   e  e eeeee e     eeeee eeeee eeeee eeee eeeee  
8e   8 8  88 8   8  8 8   8 8     8  88 8   8 8   8 8    8   8  
88   8 8   8 8e  8  8 8e  8 8e    8   8 8eee8 8e  8 8eee 8eee8e 
88   8 8   8 88  8  8 88  8 88    8   8 88  8 88  8 88   88   8 
88eee8 8eee8 88ee8ee8 88  8 88eee 8eee8 88  8 88ee8 88ee 88   8 
                                                                
                                                                                                                  
                                                             --- By Sachchidanand
                                                                                                                  
'''
    # Print the customized logo in cyan color for emphasis
    print(Fore.CYAN + logo)
    print(Fore.GREEN + "Saavn Downloader - Your Ultimate Music Downloader Tool!")
    
# Function to configure the WebDriver with enhanced aesthetics and stability
def configure_driver(headless=True, mute_audio=True):
    """Configures the Chrome WebDriver with options."""
    options = Options()
    if headless:
        options.add_argument("--headless")  # Optional: Run in headless mode (no GUI)
    options.add_argument("--disable-gpu")  # Disable GPU usage to prevent crashes in headless mode
    options.add_argument("--no-sandbox")  # Disable sandboxing for security
    if mute_audio:
        options.add_argument("--mute-audio")  # Mute audio if needed
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})  # Capture network logs

    # Initialize WebDriver with WebDriver Manager (automatically handles ChromeDriver)
    service = Service(ChromeDriverManager().install())  # Installs and manages the ChromeDriver version
    driver = webdriver.Chrome(service=service, options=options)  # Create a WebDriver instance
    return driver  # Return the configured WebDriver instance

# Function to capture network requests from the WebDriver with a more detailed log
def get_network_requests(driver):
    """Capture and print network requests, particularly related to song generation."""
    logs = driver.get_log("performance")  # Retrieve the performance logs
    print(Fore.CYAN + "\n[INFO] Capturing network requests...")

    # Iterate over each log entry
    for log_entry in logs:
        log_message = json.loads(log_entry["message"])  # Parse log entry as JSON
        message = log_message["message"]

        # Filter for requests to URLs starting with song.generateAuthToken
        if message["method"] == "Network.requestWillBeSent":
            request_url = message["params"]["request"]["url"]
            if request_url.startswith("https://www.jiosaavn.com/api.php?__call=song.generateAuthToken"):
                # If the request matches, print the URL and process the content
                print(Fore.GREEN + f"\n[INFO] Request URL: {request_url}")
                open_and_extract_content(driver, request_url)

# Function to open the URL in a new tab and extract content with detailed information
def open_and_extract_content(driver, url):
    """Open the request URL in a new tab, extract the auth_url, and download the MP4."""
    print(Fore.YELLOW + f"\n[INFO] Opening URL: {url} in a new tab...")
    driver.execute_script(f"window.open('{url}', '_blank');")  # Open the URL in a new tab
    time.sleep(3)  # Wait for the new tab to load

    # Switch to the new tab
    driver.switch_to.window(driver.window_handles[-1])

    # Get the page content (body text)
    body_content = driver.find_element(By.TAG_NAME, "body").text
    print(Fore.YELLOW + f"\n[INFO] Content from URL {url}:")
    print(Fore.YELLOW + body_content)

    # Parse the JSON response from the page content
    try:
        json_data = json.loads(body_content)  # Parse the body content as JSON
        if 'auth_url' in json_data:  # Check if 'auth_url' is present
            auth_url = json_data['auth_url']
            print(Fore.CYAN + f"\n[INFO] Auth URL found: {auth_url}")
            download_mp4(auth_url)  # Proceed to download the MP4
    except json.JSONDecodeError:
        print(Fore.RED + "[ERROR] Failed to decode JSON from the response.")

    # Close the new tab after extracting content
    driver.close()

    # Switch back to the original tab
    driver.switch_to.window(driver.window_handles[0])

# Function to download the MP4 file from the auth_url with progress bar
def download_mp4(auth_url):
    """Download the MP4 file from the provided auth_url."""
    print(Fore.MAGENTA + "\n[INFO] Downloading MP4 file...")
    response = requests.get(auth_url, stream=True)  # Make a GET request to the auth_url

    if response.status_code == 200:  # If the request is successful
        total_size = int(response.headers.get('content-length', 0))
        with open(file_name, 'wb') as file:  # Open the file in write-binary mode
            # Use tqdm for progress bar
            for data in tqdm(response.iter_content(1024), total=total_size // 1024, unit='KB', desc="Downloading"):
                file.write(data)
        print(Fore.GREEN + f"\n[INFO] MP4 file saved as {file_name}")
    else:
        print(Fore.RED + f"[ERROR] Failed to download the file. Status code: {response.status_code}")

# Function for the CLI wizard flow with smooth transitions and user interaction
def wizard_flow():
    """The interactive CLI wizard for configuring the download process."""
    clear_terminal()  # Clear terminal at the start
    print_advanced_banner()  # Print the advanced banner

    # Step 1: Ask user for a custom file name to save
    global file_name  # Declare file_name as global to be used in other functions
    file_name = input(Fore.CYAN + "[INPUT] What would you like to name the MP4 file (without extension)? ") + ".mp4"

    # Step 2: Ask user if they want headless mode
    headless_mode = input(Fore.CYAN + "[INPUT] Do you want to run in headless mode (Y/N)? ").strip().lower() == 'y'

    # Step 3: Ask user if they want to mute the audio
    mute_audio = input(Fore.CYAN + "[INPUT] Do you want to mute the audio of chrome (Y/N)? ").strip().lower() == 'y'

    # Step 4: Ask for the URL to capture network requests
    url = input(Fore.CYAN + "[INPUT] Please enter the URL of the page to capture network requests from: ").strip()

    # Step 5: Confirm settings with the user
    print(Fore.YELLOW + f"\n[INFO] You have selected the following options:\n"
                        f"File Name: {file_name}\n"
                        f"Headless Mode: {headless_mode}\n"
                        f"Mute Mode: {mute_audio}\n"
                        f"URL: {url}\n")
    
    confirm = input(Fore.CYAN + "[INPUT] Is everything correct? (Y/N): ").strip().lower()
    if confirm != 'y':
        print(Fore.RED + "[ERROR] Please restart the wizard to make changes.")
        return

    # Step 6: Start the process
    print(Fore.GREEN + "\n[INFO] Starting the download process...")

    # Configure WebDriver
    driver = configure_driver(headless_mode, mute_audio)

    try:
        driver.get(url)  # Open the URL in the browser
        print(Fore.BLUE + "[INFO] Opened the page successfully ...")
        # Wait for the page to load fully
        time.sleep(5)

        # Refresh the page
        print(Fore.BLUE + "[INFO] Refreshing the page...")
        driver.refresh()
        time.sleep(5)  # Allow time for the page to reload

        # Find the Play button and click it
        print(Fore.YELLOW + "[INFO] Attempting to find and click the play button...")
        try:
            play_button = driver.find_element(By.CSS_SELECTOR, "a.c-btn.c-btn--primary[data-btn-icon='q']")
            play_button.click()  # Click the play button
        except Exception as e:
            print(Fore.RED + f"[ERROR] Error finding play button: {e}")
        
        # Capture network requests and handle them
        get_network_requests(driver)

    except Exception as e:
        print(Fore.RED + f"[ERROR] An error occurred: {e}")
    finally:
        driver.quit()  # Close the WebDriver at the end
        logo = '''
  ________                __      __  __           
 /_  __/ /_  ____ _____  / /__    \ \/ /___  __  __
  / / / __ \/ __ `/ __ \/ //_/     \  / __ \/ / / /
 / / / / / / /_/ / / / / ,<        / / /_/ / /_/ / 
/_/ ///_///\__,_/_/ /_/_/|_|      ///\____/\__,_/  
   / ____/___  _____   __  _______(_)___  ____ _   
  / /_  / __ \/ ___/  / / / / ___/ / __ \/ __ `/   
 / __/ / /_/ / /     / /_/ (__  ) / / / / /_/ /    
/_/    \____/_/      \__,_/____/_/_/ /_/\__, /     
                                       /____/

    


'''
    # Print the customized logo in cyan color for emphasis
    print(Fore.RED + logo)
        

# Main entry point for the script
if __name__ == "__main__":
    wizard_flow()  # Start the interactive wizard flow
