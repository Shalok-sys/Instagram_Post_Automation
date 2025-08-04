import os
import time
import random
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables for secure credential storage

INSTAGRAM_USERNAME = os.getenv("INSTA_USERNAME")  
INSTAGRAM_PASSWORD = os.getenv("INSTA_PASSWORD")

# Root folder for saving files
ROOT_FOLDER = r"C:\Users\shalo\OneDrive\Desktop\Coding\InstagramAutomation"

# Path to ChromeDriver
CHROMEDRIVER_PATH = os.path.join(ROOT_FOLDER, "chromedriver.exe")

# Step 1: Traverse Directory to Find the Latest Image and Corresponding Caption
def get_latest_image_and_caption():
    logger.info("Traversing directory to find the latest image and caption pair...")
    
    # Get all files in the directory
    all_files = os.listdir(ROOT_FOLDER)
    
    # Filter for image and caption files
    image_files = [f for f in all_files if f.startswith("post_") and f.endswith(".png")]
    caption_files = [f for f in all_files if f.startswith("caption_") and f.endswith(".txt")]
    
    if not image_files:
        logger.error("No image files found in the directory.")
        return None, None
    
    if not caption_files:
        logger.error("No caption files found in the directory.")
        return None, None
    
    # Extract timestamps from image filenames
    image_timestamps = {}
    for image_file in image_files:
        try:
            timestamp = image_file[len("post_"):-len(".png")]
            image_timestamps[timestamp] = image_file
        except Exception as e:
            logger.warning(f"Failed to parse timestamp from image file {image_file}: {e}")
            continue
    
    # Extract timestamps from caption filenames
    caption_timestamps = {}
    for caption_file in caption_files:
        try:
            timestamp = caption_file[len("caption_"):-len(".txt")]
            caption_timestamps[timestamp] = caption_file
        except Exception as e:
            logger.warning(f"Failed to parse timestamp from caption file {caption_file}: {e}")
            continue
    
    # Find matching pairs of image and caption files
    matching_timestamps = set(image_timestamps.keys()) & set(caption_timestamps.keys())
    if not matching_timestamps:
        logger.error("No matching image and caption pairs found.")
        return None, None
    
    # Sort timestamps to find the latest pair
    latest_timestamp = sorted(matching_timestamps, reverse=True)[0]
    latest_image_file = image_timestamps[latest_timestamp]
    latest_caption_file = caption_timestamps[latest_timestamp]
    
    # Construct full paths
    image_path = os.path.join(ROOT_FOLDER, latest_image_file)
    caption_path = os.path.join(ROOT_FOLDER, latest_caption_file)
    
    # Read the caption
    try:
        with open(caption_path, "r") as f:
            caption = f.read().strip()
    except Exception as e:
        logger.error(f"Failed to read caption file {caption_path}: {e}")
        return None, None
    
    logger.info(f"Latest image: {image_path}")
    logger.info(f"Corresponding caption: {caption}")
    return image_path, caption

# Step 2: Publish to Instagram using Selenium
def publish_to_instagram(image_path, caption, retries=2):
    logger.info("Starting Instagram posting process...")
    for attempt in range(retries + 1):
        driver = None
        try:
            # Set up ChromeDriver in headless mode
            service = Service(CHROMEDRIVER_PATH)
            options = webdriver.ChromeOptions()
            # options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.7103.114 Safari/537.36")
            driver = webdriver.Chrome(service=service, options=options)
            
            # Step 2.1: Open Instagram and log in
            logger.info("Navigating to Instagram...")
            driver.get("https://www.instagram.com/")
            time.sleep(random.uniform(3, 5))
            
            # Enter username
            logger.info("Entering username...")
            username_field = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_field.send_keys(INSTAGRAM_USERNAME)
            time.sleep(random.uniform(1, 2))
            
            # Enter password
            logger.info("Entering password...")
            password_field = driver.find_element(By.NAME, "password")
            password_field.send_keys(INSTAGRAM_PASSWORD)
            time.sleep(random.uniform(1, 2))
            
            # Click login button
            logger.info("Clicking login button...")
            login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            time.sleep(random.uniform(5, 7))
            
            # Handle "Save Your Login Info?" prompt
            try:
                logger.info("Checking for save login info prompt...")
                not_now_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Not Now')]"))
                )
                not_now_button.click()
                time.sleep(random.uniform(2, 3))
            except TimeoutException:
                logger.info("Save login info prompt not found, proceeding...")
            
            # Handle "Turn on Notifications?" prompt
            try:
                logger.info("Checking for notifications prompt...")
                not_now_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Not Now')]"))
                )
                not_now_button.click()
                time.sleep(random.uniform(2, 3))
            except TimeoutException:
                logger.info("Notifications prompt not found, proceeding...")

            # Step 2.1: Make sure to click ok when sleep mode pop up is there.
            try:
                logger.info("Checking for 'You're in sleep mode' popup...")
                
                # Wait for the popup to appear and for the OK button to be clickable
                ok_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "div[role='dialog'] button"))
                )
                
                # Optional: validate the button text just to be sure
                if ok_button.text.strip().lower() == "ok":
                    ok_button.click()
                    logger.info("'Sleep mode' popup dismissed.")
                    time.sleep(1)
                else:
                    logger.warning("Found button, but label is not 'OK': %s", ok_button.text)

            except TimeoutException:
                logger.info("No 'sleep mode' popup detected, continuing...")
            
            # Step 2.2: Click the "Create" button to start a new post
            logger.info("Clicking Create button...")
            create_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "svg[aria-label='New post']"))
            )
            create_button.click()
            time.sleep(random.uniform(2, 3))
            

            # Step 2.3: Click "Post" in the dropdown menu after clicking Create
            logger.info("Clicking 'Post' option in the dropdown...")

            # Wait for the dropdown to appear and find the "Post" option
            post_option = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//span[text()='Post' or normalize-space()='Post']"
                ))
            )
            post_option.click()
            time.sleep(random.uniform(2, 3))

            
            # Step 2.4: Click "Select from Computer"
            logger.info("Clicking Select from Computer...")
            select_from_computer_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Select from computer')]"))
            )
            select_from_computer_button.click()
            time.sleep(random.uniform(2, 3))
            
            # Step 2.5: Upload the latest image
            logger.info(f"Uploading image: {image_path}...")
            file_input = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
            )
            file_input.send_keys(image_path)
            time.sleep(random.uniform(3, 5))
            
            # Step 2.6: Click "Next" to proceed to the edit screen
            logger.info("Clicking Next (edit screen)...")
            next_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Next')]"))
            )
            next_button.click()
            time.sleep(random.uniform(2, 3))
            
            # Step 2.7: Click "Next" again to proceed to the caption screen
            logger.info("Clicking Next (caption screen)...")
            next_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Next')]"))
            )
            next_button.click()
            time.sleep(random.uniform(2, 3))
            
            # Step 2.8: Enter the caption
            logger.info("Entering caption...")
            try:
                # Try multiple selectors for the caption field
                caption_field = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, 
                        "//textarea[contains(@placeholder, 'caption')] | "
                        "//textarea[contains(@aria-label, 'Write a caption...')] | "
                        "//div[@contenteditable='true' and contains(@aria-label, 'caption')]"))
                )
                # Clear the field (if needed) and enter the caption
                caption_field.clear()
                caption_field.send_keys(caption)
                logger.info(f"Caption entered: {caption}")
            except TimeoutException:
                logger.error("Failed to find the caption field. Dumping page source for debugging...")
                logger.debug(driver.page_source)
                raise
            
            time.sleep(random.uniform(2, 3))
            
            # Step 2.9: Click "Share" to post
            logger.info("Clicking Share button...")
            share_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Share')]"))
            )
            share_button.click()
            time.sleep(random.uniform(5, 7))
            
            # Wait for the post to complete
            logger.info("Successfully posted to Instagram!")
            return True
            
        except (TimeoutException, WebDriverException) as e:
            logger.error(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries:
                logger.info("Retrying after a delay...")
                time.sleep(30)
            else:
                logger.error("Max retries reached. Failed to publish to Instagram.")
                return False
        finally:
            if driver:
                try:
                    driver.quit()
                    logger.info("Browser closed.")
                except:
                    logger.warning("Failed to close browser.")
# Main Workflow
def main():
    # Get the latest image and corresponding caption
    image_path, caption = get_latest_image_and_caption()
    if not image_path or not caption:
        print("Failed to find a matching image and caption pair.")
        return
    
    print("Latest Image:", image_path)
    print("Corresponding Caption:", caption)
    
    # Derive the caption file path from the image path
    timestamp = os.path.basename(image_path)[len("post_"):-len(".png")]
    caption_path = os.path.join(ROOT_FOLDER, f"caption_{timestamp}.txt")
    
    # Publish to Instagram with safety measures
    if publish_to_instagram(image_path, caption):
        print("Post published successfully!")
        
        # Delete the image and caption files after successful posting
        try:
            logger.info(f"Deleting image file: {image_path}")
            os.remove(image_path)
            logger.info(f"Image file {image_path} deleted successfully.")
        except Exception as e:
            logger.error(f"Failed to delete image file {image_path}: {e}")
        
        try:
            logger.info(f"Deleting caption file: {caption_path}")
            os.remove(caption_path)
            logger.info(f"Caption file {caption_path} deleted successfully.")
        except Exception as e:
            logger.error(f"Failed to delete caption file {caption_path}: {e}")
        
        print("Waiting 24 hours before the next post to avoid detection...")
        time.sleep(86400)
    else:
        print("Failed to publish post.")

if __name__ == "__main__":
    main()