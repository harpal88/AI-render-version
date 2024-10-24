import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from login1 import (
    open_vidu_and_sign_in,
    login_to_tutanota_and_get_otp,
    enter_otp
)
from login2 import (
    close_notification_if_present,
    click_create_video_link,
    enter_prompt,
    upload_file,
    wait_for_create_button_and_click,
    download_from_last_div
)

# def login_to_vidu(driver):
#     try:
#         # Open Vidu and Tutanota
#         driver.execute_script("window.open('');")
#         vidu_tab = driver.window_handles[0]
#         tutanota_tab = driver.window_handles[1]

#         # Open Vidu and check the current URL
#         driver.switch_to.window(vidu_tab)
#         driver.get("https://www.vidu.studio/create/img2video")  # Navigate to the img2video page

#         # Check if the user is logged in by inspecting the URL
#         if "login" in driver.current_url:
#             print("User is not logged in, proceeding with login...")
#             open_vidu_and_sign_in(driver)  # Login process
#             # Open Tutanota and retrieve OTP
#             driver.switch_to.window(tutanota_tab)
#             otp_code = login_to_tutanota_and_get_otp(driver)

#             if otp_code:
#                 driver.switch_to.window(vidu_tab)
#                 enter_otp(driver, otp_code)
#                 return True  # Login success
#             else:
#                 print("Failed to retrieve OTP Code.")
#                 return False  # Login failed
#         else:
#             print("User is already logged in.")
#             return True  # Already logged in
#     except Exception as e:
#         print(f"An error occurred during login: {e}")
#         return False

def login_to_vidu(driver):
    try:
        # Open Vidu and Tutanota
        driver.execute_script("window.open('');")
        vidu_tab = driver.window_handles[0]
        tutanota_tab = driver.window_handles[1]

        # Open Vidu and navigate to the img2video page
        driver.switch_to.window(vidu_tab)
        driver.get("https://www.vidu.studio")  # Navigate to the img2video page

        # Check if the necessary cookies (JWT and Shunt) are already present
        cookies_present = all(driver.get_cookie(name) for name in ['JWT', 'Shunt'])

        if cookies_present:
            print("Required cookies are already present. User is logged in.")
            return True  # User is already logged in
        else:
            print("Cookies not present, adding cookies to log in...")

            # Add JWT and other necessary cookies
            cookies = [
                {
                    "domain": ".vidu.studio",
                    "name": "JWT",
                    "value": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Mjk3OTMwODMsImlhdCI6MTcyODQ5NzA4MywiaXNzIjoiaWFtIiwic3ViIjoiMjQ2ODI0NzYzNzU5OTI1NiJ9.urEITHxlk1x-jIvyeNf3KaxP01r39uHofgqSZAdT2kU",
                    "path": "/",
                    "httpOnly": True,
                    "secure": True
                },
                {
                    "domain": ".vidu.studio",
                    "name": "Shunt",
                    "value": "",
                    "path": "/",
                    "httpOnly": True,
                    "secure": True
                }
            ]

            # Loop through the cookies and add them to the browser
            for cookie in cookies:
                driver.add_cookie(cookie)

            # Refresh the page to apply cookies
            driver.refresh()
            print("Cookies added and page refreshed.")

            # Verify login by checking if cookies are now present
            driver.implicitly_wait(10)  # Adjust wait time as needed
            cookies_present = all(driver.get_cookie(name) for name in ['JWT', 'Shunt'])

            if cookies_present:
                print("User logged in successfully after adding cookies.")
                return True  # Login success
            else:
                print("Login failed after adding cookies.")
                return False  # Login failed
    except Exception as e:
        print(f"An error occurred during login: {e}")
        return False

# Encapsulate the Vidu process (creating video, uploading file, downloading video)
def vidu_process(driver, file_path, download_dir, prompt):
    try:
        # Close notification if present
        close_notification_if_present(driver)

        # Click "Create Video" link
        click_create_video_link(driver)

        # Enter the prompt
        enter_prompt(driver, prompt)

        # Upload the image
        upload_file(driver, file_path)

        # Click "Create" button
        wait_for_create_button_and_click(driver)

        # Download the last video
        download_from_last_div(driver, download_dir)

    except Exception as e:
        print(f"An error occurred during the Vidu process: {e}")

# You can remove the `if __name__ == "__main__":` section if it’s not needed,
# as you are running everything through `app.py` now.
