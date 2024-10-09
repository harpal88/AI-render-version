from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from selenium.common.exceptions import TimeoutException




# Function to close notification if present
def close_notification_if_present(driver):
    try:
        time.sleep(2)  # Wait for notifications to appear
        close_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//button[contains(@class, "absolute top-8 right-8")]'))
        )
        if close_button.is_displayed():
            close_button.click()
            print("Notification closed.")
        else:
            print("No notification to close.")
    except Exception as e:
        print(f"Error while checking for close button: {e}")

# Function to click "Create Video" link
def click_create_video_link(driver):
    try:
        create_video_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//a[@href="/create" and contains(text(), "Create Video")]'))
        )
        create_video_link.click()
        print("Clicked 'Create Video' link.")
        time.sleep(5)  # Wait for the page to load
    except Exception as e:
        print(f"Error clicking 'Create Video' link: {e}")

# Function to enter the prompt
def enter_prompt(driver, prompt):
    try:
        textarea = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.CSS_SELECTOR, 'textarea[class*="flex"]'))
)

        textarea.clear()
        textarea.send_keys(prompt)
        print(f"Entered prompt: {prompt}")
    except Exception as e:
        print(f"Error while entering prompt: {e}")

# Function to upload the image file
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
import time

def upload_file(driver, file_path):
    try:
        # Proceed with file upload
        for attempt in range(3):  # Try up to 3 times
            try:
                file_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"][accept="image/jpeg, image/png"]'))
                )
                file_input.send_keys(file_path)
                print(f"Uploaded file: {file_path}")
                return  # Exit after successful upload
            except StaleElementReferenceException:
                print("Stale element reference. Retrying...")

        print("Failed to upload file after multiple attempts.")
    except Exception as e:
        print(f"Error while uploading file: {e}")



from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

# Function to wait for the "Create" button and click
def wait_for_create_button_and_click(driver):
    max_wait_time = 300  # Maximum total wait time in seconds (5 minutes)
    polling_interval = 5  # Check every 5 seconds
    total_waited = 0

    try:
        # Loop to wait for the button to be enabled and visible
        while total_waited < max_wait_time:
            try:
                # Wait for the button span containing "Create" to be present
                create_span = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, '//span[text()="Create"]'))
                )

                # Get the button element (closest 'button' parent of the span)
                create_button = driver.execute_script(
                    "return arguments[0].closest('button');", create_span
                )

                # Check if the button is enabled and visible
                if create_button and create_button.get_attribute('aria-disabled') == 'false':
                    print("Button is enabled and visible, attempting to click...")

                    # Check if the button is displayed in the UI
                    if create_button.is_displayed():
                        create_button.click()  # Click the button
                        print("Successfully clicked 'Create' button.")
                        return True
                    else:
                        print("Button is not displayed.")
                else:
                    print("Button is disabled or not found. Retrying...")

            except TimeoutException:
                print("Create button is not yet available. Retrying...")

            # Increment the wait time and wait for the next polling interval
            total_waited += polling_interval
            time.sleep(polling_interval)

        print(f"Failed to click 'Create' button after {max_wait_time} seconds.")

    except Exception as e:
        print(f"Error clicking the 'Create' button: {e}")

    return False







# Function to download the last video (optional)
def download_from_last_div(driver, download_dir):

    time.sleep(10)  # Optional: wait before retrying

    # Wait for the container with the specified classes to load
    divs = WebDriverWait(driver, 520).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.my-8.flex.gap-8.lg\\:my-5.md\\:my-5.xl\\:my-7'))
    )
    
    # Get the last div
    last_div = divs[-1]

    # Wait for the xgplayer-start element to be clickable
    xgplayer_start = WebDriverWait(last_div, 520).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'xgplayer-start'))
    )
    xgplayer_start.click()
    print("played")

    # Click on the xgplayer-download element
    download_link = last_div.find_element(By.CSS_SELECTOR, 'xg-icon.xgplayer-download[data-index="3"] a')
    download_link.click()
    time.sleep(2)  # Optional: wait before retrying
    