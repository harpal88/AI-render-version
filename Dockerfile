# Base image
FROM python:3.9-slim

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg \
    libnss3 \
    libgconf-2-4 \
    libxss1 \
    libappindicator3-1 \
    fonts-liberation \
    libu2f-udev \
    xdg-utils \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver
RUN CHROME_DRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip" && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip

# Set environment variables
ENV PORT=5000
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99  
ENV FLASK_APP=app.py

# Set up application directory
WORKDIR /app

# Copy the application code
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories for uploads, output, and results (if not present)
RUN mkdir -p /app/instance/uploads /app/instance/output_folder /app/instance/results

# Set permissions (Optional, depends on how you manage these directories)
RUN chmod -R 755 /app/instance

# Expose the port Flask will run on
EXPOSE $PORT

# Start the app using Flask's run command
CMD ["sh", "-c", "flask run --host=0.0.0.0 --port=${PORT}"]
