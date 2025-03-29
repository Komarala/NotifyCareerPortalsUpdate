import requests
from bs4 import BeautifulSoup
import hashlib
import time
import schedule
import pandas as pd
import ast
from pushbullet import Pushbullet
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Pushbullet API key (sign up at https://www.pushbullet.com/ to get the key)
API_KEY = ''

# Initialize Pushbullet instance
pb = Pushbullet(API_KEY)

# Function to get the current page content for static pages
def get_static_page_content():
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Modify the selector according to the HTML structure of the page
    job_listings = soup.find_all('div', class_='job-listing')  # Example selector
    job_text = ''.join([str(job) for job in job_listings])
    return job_text

# Function to get the current page content for dynamic pages (using Selenium)
def get_dynamic_page_content():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (no browser UI)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(url)
    time.sleep(5)  # Wait for JavaScript to load content (adjust as needed)

    # Modify the selector according to the HTML structure of the page
    job_listings = driver.find_elements(By.CLASS_NAME, 'job-listing')  # Example selector
    job_text = ''.join([listing.text for listing in job_listings])
    driver.quit()
    return job_text

# Function to send a notification using Pushbullet
def send_notification(message):
    pb.push_note("Careers Portal Update", message)

# Function to compare and detect changes
def check_for_updates():
    # Try to get content using the static method first
    try:
        current_content = get_static_page_content()
    except Exception:
        # If static content method fails, fall back to dynamic method (Selenium)
        current_content = get_dynamic_page_content()

    # Load the previously stored content (if any)
    try:
        with open('last_content_hash.txt', 'r') as file:
            last_content_hash = file.read().strip()
    except FileNotFoundError:
        last_content_hash = ''

    # Generate the hash of the current content
    current_hash = hashlib.md5(current_content.encode()).hexdigest()

    # Compare the hash of the current content with the previous one
    if current_hash != last_content_hash:
        send_notification("The careers portal has been updated!")

        # Save the new hash
        with open('last_content_hash.txt', 'w') as file:
            file.write(current_hash)


# Step 1: Read the Excel file into a DataFrame
try:
    df = pd.read_excel('your_file.xlsx', sheet_name='Sheet1')
except Exception as e:
    print(f"Error reading Excel file: {e}")
    exit(1)

# Step 2: Iterate over each row and calculate the new value for the adjacent cell
for idx, row in df.iterrows():
    try:
        # Read the value from the 'InputColumn' (assuming numeric data)
        input_value = row['InputColumn']

        # Call the external function to calculate the new value
        calculated_value = check_for_updates(input_value)

        # Write the calculated value to the adjacent 'CalculatedColumn'
        df.at[idx, 'CalculatedColumn'] = calculated_value

    except Exception as e:
        print(f"Error processing row {idx}: {e}")
        # You can either set a default value or leave it empty for rows where calculation fails
        df.at[idx, 'CalculatedColumn'] = None

# Step 3: Save the updated DataFrame back to the Excel file
try:
    df.to_excel('your_file_updated.xlsx', sheet_name='Sheet1', index=False)
    print("File updated successfully.")
except Exception as e:
    print(f"Error saving Excel file: {e}")