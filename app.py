import cv2
from flask import Flask, request, render_template, redirect, url_for, send_from_directory, session
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from frames import extract_frames
from main import login_to_vidu, vidu_process
from flask_session import Session  # Import Flask-Session

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management
app.config['SESSION_TYPE'] = 'filesystem'  # Configure session type
Session(app)  # Initialize the session

# Paths
UPLOAD_FOLDER = os.path.join(app.instance_path, 'uploads')
OUTPUT_FOLDER = os.path.join(app.instance_path, 'output_folder')
VIDEO_OUTPUT_FOLDER = os.path.join(app.instance_path, 'results')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['VIDEO_OUTPUT_FOLDER'] = VIDEO_OUTPUT_FOLDER  # Register the new folder in the app config
import os

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(VIDEO_OUTPUT_FOLDER, exist_ok=True)

# Global variable to store the driver
driver = None

# Setup the WebDriver
# Setup the WebDriver
def setup_driver():
    chrome_options = Options()

    # Specify the path to the Chrome binary, as the system may look for Chromium by default.
    chrome_options.binary_location = "/usr/bin/google-chrome"

    # Add necessary Chrome options for running in headless mode
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode
    chrome_options.add_argument("--no-sandbox")  # Recommended for running as root in containers
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration (optional)
    chrome_options.add_argument("--disable-extensions")  # Disable extensions (optional)
    chrome_options.add_argument("--window-size=1920,1080")  # Set window size (optional but useful for consistency)

    # Set download preferences
    prefs = {
        "download.default_directory": app.config['VIDEO_OUTPUT_FOLDER'],  # Set the folder for downloads
        "download.prompt_for_download": False,  # Do not prompt for downloads
        "download.directory_upgrade": True,  # Allow directory changes without user input
        "safebrowsing.enabled": True,  # Enable safe browsing
        "profile.default_content_setting_values.notifications": 2,  # Block notifications
        "profile.content_settings.exceptions.automatic_downloads.*.setting": 1  # Allow automatic downloads
    }
    chrome_options.add_experimental_option("prefs", prefs)

    # Create the WebDriver using ChromeDriver and options
    return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)


@app.route('/')
def index():
    # Render index.html for both logged-in and not-logged-in users
    # Pass login status to the template to control what content is displayed
    if 'logged_in' in session and session['logged_in']:
        return render_template('index.html', logged_in=True)  # User is logged in
    else:
        return render_template('index.html', logged_in=False)  # User is not logged in

from datetime import timedelta

app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)  # Session valid for 1 day
app.secret_key = 'your_secret_key'  # Make sure this is set

# Endpoint for login
@app.route('/login', methods=['POST'])
def login():
    global driver
    if driver is None:  # Setup the driver only once
        driver = setup_driver()

    login_success = login_to_vidu(driver)

    if login_success:
        session.permanent = True  # Make the session permanent
        session['logged_in'] = True  # Set session variable to indicate user is logged in
        return {"message": "Login successful"}, 200
    else:
        print("Login failed, resetting driver and session.")

        session.clear()  # Clear all session data

        if driver is not None:
            driver.quit()  # Quit the current driver instance
            driver = None  # Reset driver to None so it can be reinitialized

        return {"message": "Login failed. Please try again."}, 400
@app.route('/check_login', methods=['GET'])
def check_login():
    return {"logged_in": session.get('logged_in', False)}, 200


@app.route('/logout')
def logout():
    global driver
    session.clear()  # Clear the session
    if driver is not None:
        driver.quit()  # Quit the WebDriver when the user logs out
        driver = None
    return redirect(url_for('index'))  # Redirect to login page after logout


# Endpoint for uploading an image
import glob

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return {"error": "No file part"}, 400

    file = request.files['file']

    if file.filename == '':
        return {"error": "No selected file"}, 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Get the prompt from the request
    prompt = request.form.get('prompt')

    if driver:
        # Pass VIDEO_OUTPUT_FOLDER to save the video to the correct folder
        vidu_process(driver, file_path, app.config['VIDEO_OUTPUT_FOLDER'], prompt)

        # Find the most recently created video file
        video_files = glob.glob(os.path.join(app.config['VIDEO_OUTPUT_FOLDER'], '*.mp4'))  # Adjust file extension if needed

        if not video_files:
            return {"error": "No video files found."}, 404
        
        latest_video = max(video_files, key=os.path.getmtime)  # Get the latest video file based on modification time

        # Extract frames from the processed video
        extract_frames(latest_video, app.config['OUTPUT_FOLDER'], interval=0.65)

        return {"message": "Video processed and frames extracted successfully."}, 200
    else:
        return {"error": "Driver not initialized!"}, 400


@app.teardown_appcontext
def shutdown_driver(exception=None):
    global driver
    if driver is not None and exception is not None:
        driver.quit()  # Close the driver if an exception occurs

# Endpoint for displaying the created image
@app.route('/output_frames/<filename>')
def show_image(filename):
    file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_from_directory(app.config['OUTPUT_FOLDER'], filename)
    else:
        print(f"File not found: {file_path}")  # Log missing files
        return {"error": "File not found"}, 404  # Return JSON error instead of HTML

# Endpoint for listing images
@app.route('/list_images', methods=['GET'])
def list_images():
    try:
        # List all image files in the output folder
        image_files = [f for f in os.listdir(app.config['OUTPUT_FOLDER']) if f.endswith(('.jpg', '.jpeg', '.png', '.gif'))]
        image_urls = [url_for('show_image', filename=filename) for filename in image_files]  # Create URLs for each image

        return {"images": image_urls}, 200
    except Exception as e:
        print(f"Error fetching images: {e}")
        return {"error": "Could not fetch images"}, 500  # Return a JSON error response

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))  # Use PORT environment variable or default to 5000
    app.run(host='0.0.0.0', port=port, debug=True)  # 