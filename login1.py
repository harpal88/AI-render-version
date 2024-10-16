from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
import subprocess  # Add this import at the top of your script
from selenium.webdriver.chrome.options import Options

# Constants for Vidu and Tutanota credentials
VIDU_LOGIN_URL = 'https://www.vidu.studio/login'
TUTANOTA_EMAIL = 'harpalsinh798@tutamail.com'
TUTANOTA_PASSWORD = 'WyF2b7QytJwfv4p'

# def close_notification_if_present(driver):
#     try:
#         # Wait for a few seconds to allow any notifications to appear
#         time.sleep(2)  # Adjust the wait time if needed

#         # Check for the notification close button and click it if present
#         close_button = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, 'button[class*="close"], button[class*="dismiss"]'))
#         )
        
#         if close_button.is_displayed():
#             close_button.click()
#             print("Clicked the notification close button.")
#         else:
#             print("Notification close button is not displayed.")
#     except Exception as e:
#         print(f"Error while closing notification: {e}")

def retrieve_and_click_email(driver):
    try:
        # Close notification if present
        # close_notification_if_present(driver)

        # Wait for the inbox (ul.list.rel.click) to be visible on the screen
        inbox_list = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'ul.list.rel.click'))
        )

        print("Inbox loaded and visible. Searching for the first email...")

        # Locate all <li> elements that contain emails
        email_items = inbox_list.find_elements(By.TAG_NAME, 'li')

        if email_items:
            first_email = email_items[0]
            
            # Scroll to the first email to make sure it's in the viewport
            driver.execute_script("arguments[0].scrollIntoView();", first_email)
            time.sleep(1)  # Add a slight delay after scrolling
            
            # Wait until the email is interactable (clickable)
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(first_email)
            )
            
            # Click the first email
            first_email.click()
            print(f"Clicked on the first email: {first_email.text}")
            return True
        else:
            print("No emails found in the inbox.")
            return False

    except Exception as e:
        print(f"Error in retrieving or clicking email: {e}")
        return False


def wait_for_inbox_to_load(driver, max_wait_time=120, check_interval=5):
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        try:
            inbox_list = WebDriverWait(driver, check_interval).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.list.rel.click'))
            )
            print("Inbox loaded successfully.")
            return inbox_list  # Return the loaded inbox list
        except Exception as e:
            print("Waiting for inbox to load...")
            time.sleep(check_interval)  # Wait before checking again

    print("Failed to load inbox within the specified time.")
    return None  # Return None if inbox didn't load in time

# Function to log in to Tutanota and retrieve OTP
def login_to_tutanota_and_get_otp(driver):
    try:
        # Open Tutanota login page
        driver.get("https://mail.tutanota.com/login")
        time.sleep(5)  # Wait for the page to load
        
        # Input email and password
        email_input = driver.find_element(By.XPATH, '//input[@type="email"]')
        email_input.send_keys(TUTANOTA_EMAIL)
        
        password_input = driver.find_element(By.XPATH, '//input[@type="password"]')
        password_input.send_keys(TUTANOTA_PASSWORD)

        # Click the log in button
        login_button = driver.find_element(By.XPATH, '//button[contains(text(), "Log in")]')
        login_button.click()
        
        print("Logged into Tutanota. Waiting for inbox to load...")

        # Call the function to wait until the inbox list is loaded
        inbox_list = wait_for_inbox_to_load(driver, max_wait_time=120)  # Adjust max_wait_time as needed

        if inbox_list:
            print("Inbox is now visible. Proceeding to click the first email...")
            if not retrieve_and_click_email(driver):
                print("Failed to find matching email.")
                return None
        else:
            print("Inbox failed to load.")
            return None

        otp_code = None  # Initialize otp_code to None
        
        # Start checking for the OTP in a loop
        while True:
            try:
                # Wait for the email content to load
                email_content_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'body'))
                )

                # Extract the whole page text
                page_text = email_content_element.text

                # Search for a 6-digit number in the page content using regex
                otp_match = re.search(r'\b\d{6}\b', page_text)
                
                if otp_match:
                    otp_code = otp_match.group(0)
                    print(f"Successfully retrieved the 6-digit OTP code: {otp_code}")
                    break  # Exit loop once verification code is found
                else:
                    print("Waiting for the verification code...")  # Provide a status message
                    time.sleep(2)  # Wait before checking again

            except Exception as e:
                print(f"Error while retrieving OTP: {e}")
                time.sleep(2)  # Check again after 2 seconds

    finally:
        return otp_code  # Return the found OTP code



def open_vidu_and_sign_in(driver):
    try:
        # Open Vidu's login page
        driver.get(VIDU_LOGIN_URL)
        time.sleep(5)  # Allow time for the page to load
        
        # Find and click the "Sign in with Email" button
        sign_in_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Sign in with Email")]'))
        )
        sign_in_button.click()
        print("Clicked on 'Sign in with Email' button.")

        # Wait for the email input field to appear
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Email address"]'))
        )
        
        # Enter the Tutanota email address
        email_input.send_keys(TUTANOTA_EMAIL)
        print(f"Entered email: {TUTANOTA_EMAIL}")

        # Click the "Next" button
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Next")]'))
        )
        next_button.click()
        print("Clicked on 'Next' button.")

    except Exception as e:
        print(f"Error during Vidu sign-in: {e}")

def enter_otp(driver, verification_code):
    try:
        # Wait for the OTP input field to be visible
        otp_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//input[@data-input-otp="true"]'))
        )

        # Clear the OTP input field if needed
        otp_input.clear()

        # Type each digit of the verification code into the input field one by one
        for digit in verification_code:
            otp_input.send_keys(digit)
            time.sleep(0.5)  # Optional: short delay to simulate typing

        print("Successfully entered the OTP.")
    except Exception as e:
        print(f"Error while entering OTP: {e}")

def check_and_close(driver):
    try:
        # Wait for a few seconds to ensure the page is loaded
        time.sleep(5)
        
        # Check if the close button is present
        close_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'button[class*="absolute"][class*="top-8"][class*="right-8"]'))
        )
        
        # If the close button is found, click it
        close_button.click()
        print("Clicked the close button.")
        
    except Exception as e:
        print("Close button not found or couldn't be clicked:", e)
