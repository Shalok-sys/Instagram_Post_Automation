import requests
from PIL import Image, ImageDraw, ImageFont
import io
import os
from datetime import datetime
import certifi
import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Root folder for saving files
ROOT_FOLDER = os.getcwd()

INSTAGRAM_USERNAME = os.getenv("INSTA_USERNAME")  
INSTAGRAM_PASSWORD = os.getenv("INSTA_PASSWORD")

# Root folder for saving files
ROOT_FOLDER = os.getcwd()

# Path to ChromeDriver (update this to your ChromeDriver location)
CHROMEDRIVER_PATH = os.path.join(ROOT_FOLDER, "chromedriver.exe")  # On Windows, use "chromedriver.exe"

# List of themes for quotes
QUOTE_THEMES = ["bold", "inspiring", "positive", "resilient", "uplifting"]

# List of famous people (Stoics, Greek philosophers, and other notable figures with many quotes)
FAMOUS_PEOPLE = [
    "Marcus Aurelius", "Seneca", "Epictetus", "Zeno of Citium",  # Stoics
    "Socrates", "Plato", "Aristotle", "Heraclitus", "Diogenes", "Epicurus",  # Greek philosophers
    "Confucius", "Lao Tzu",  # Chinese philosophers
    "Ralph Waldo Emerson", "Henry David Thoreau",  # Transcendentalists
    "Maya Angelou", "Albert Einstein", "Nelson Mandela", "Mahatma Gandhi",  # Modern inspirational figures
    "Rumi", "Kahlil Gibran",  # Poets and mystics
    "Winston Churchill", "Abraham Lincoln", "Martin Luther King Jr.",  # Historical leaders
    "Friedrich Nietzsche", "Søren Kierkegaard", "Immanuel Kant",  # Existentialists and philosophers
    "Viktor Frankl", "Carl Jung", "Sigmund Freud",  # Psychologists and thinkers
    "Eleanor Roosevelt", "Helen Keller", "Anne Frank"  # Inspirational women
]

# List of creative art themes for images
IMAGE_THEMES = [
    "surrealist dreamscape with vibrant colors and a soft gradient sky for text overlay",
    "minimalist mountain landscape at sunrise with a pastel sky and open space",
    "a calm ocean horizon with warm sunlight and smooth color transitions",
    "soft-focus forest glade with light beams and open misty airspace for text",
    "aerial view of a desert dune with flowing sand patterns and empty central focus",
    "cosmic galaxy scene with stars and nebulae forming a subtle swirl around a dark center",
    "open field of sunflowers under a clear sky with depth and gentle contrast",
    "abstract pastel gradient background with flowing waves and central light zone",
    "misty hill silhouette in monochrome with a wide sky above",
    "dreamy cloudscape in golden hour lighting with light bokeh and sky openness"
]


# Step 1: Generate Motivational Text and Caption using Pollinations.AI
def generate_motivational_content():
    # Randomly select a theme and person
    theme = random.choice(QUOTE_THEMES)
    person = random.choice(FAMOUS_PEOPLE)
    timestamp = int(datetime.now().timestamp())  # Unix timestamp for seed
    
    # Construct the prompt with the person's name and seed
    prompt = f"A {theme} motivational quote by {person}, followed by a caption and descryption/context with hashtags. Separate quote and caption with a newline. (seed: {timestamp})"
    encoded_prompt = prompt.replace(" ", "%20").replace("\n", "%0A")
    cache_bust = random.randint(1000, 9999)
    text_url = f"https://text.pollinations.ai/{encoded_prompt}?cache_bust={cache_bust}"
    
    try:
        response = requests.get(text_url, verify=certifi.where())
        if response.status_code == 200:
            text = response.text.strip()
            quote, caption = text.split("\n", 1) if "\n" in text else (text, f"Stay {theme}! #Motivation #InspireDaily")
            # Ensure the person's name is in the quote
            if person not in quote:
                quote = f"{quote} - {person}"
            return quote, caption
        else:
            print("Pollinations text API error:", response.status_code, response.text)
            return f"Keep going! - {person}", f"Stay {theme}! #Motivation #InspireDaily"
    except Exception as e:
        print("Pollinations text API failed:", e)
        return f"Keep going! - {person}", f"Stay {theme}! #Motivation #InspireDaily"

# Step 2: Generate Aesthetic Image using Pollinations.AI and Remove Watermark
def generate_aesthetic_image():
    # Add randomness with a creative art theme, timestamp-based seed, and cache bust
    theme = random.choice(IMAGE_THEMES)
    timestamp = int(datetime.now().timestamp())
    prompt = f"{theme} background for Instagram post, serene aesthetic (seed: {timestamp})"
    encoded_prompt = prompt.replace(" ", "%20")
    cache_bust = random.randint(1000, 9999)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1080&seed={timestamp}&cache_bust={cache_bust}"
    
    try:
        response = requests.get(image_url, verify=certifi.where())
        if response.status_code == 200:
            image_data = response.content
            image = Image.open(io.BytesIO(image_data))
            # Crop the bottom-right section to remove the watermark
            # Assuming watermark is in the bottom 50 pixels and right 200 pixels
            width, height = image.size
            crop_box = (0, 0, width - 200, height - 50)  # Left, Top, Right, Bottom
            cropped_image = image.crop(crop_box)
            # Resize back to 1080x1080 to maintain Instagram resolution
            resized_image = cropped_image.resize((1080, 1080), Image.Resampling.LANCZOS)
            return resized_image
        else:
            print("Pollinations image API error:", response.status_code, response.text)
            return Image.new("RGB", (1080, 1080), color="#E6E6FA")
    except Exception as e:
        print("Pollinations image API failed:", e)
        return Image.new("RGB", (1080, 1080), color="#E6E6FA")

# Step 3: Merge Text onto Image using Pillow with Consistent Font
def merge_text_on_image(image, text):
    draw = ImageDraw.Draw(image)
    # Load Roboto font consistently (place roboto.ttf in root folder)
    font_path = os.path.join(ROOT_FOLDER, "Montserrat-SemiBold.ttf")
    try:
        # Adjust font size based on quote length for readability
        quote_length = len(text)
        if quote_length <= 30:
            font_size = 60
        elif quote_length <= 50:
            font_size = 50
        else:
            font_size = 40
        font = ImageFont.truetype(font_path, font_size) if os.path.exists(font_path) else ImageFont.truetype("arial.ttf", font_size)
    except Exception as e:
        print("Font loading failed:", e)
        font = ImageFont.load_default()
    
    # Split text into lines for better wrapping
    max_width = 900
    lines = []
    words = text.split()
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        test_bbox = draw.textbbox((0, 0), test_line, font=font)
        if test_bbox[2] - test_bbox[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line.strip())
            current_line = word + " "
    lines.append(current_line.strip())
    
    # Calculate total text height
    line_height = (draw.textbbox((0, 0), "A", font=font)[3] - draw.textbbox((0, 0), "A", font=font)[1]) + 10
    total_text_height = len(lines) * line_height
    
    # Center text on image
    width, height = image.size
    y = (height - total_text_height) // 2
    
    # Draw text with shadow
    shadow_offset = 2
    for line in lines:
        line_bbox = draw.textbbox((0, 0), line, font=font)
        line_width = line_bbox[2] - line_bbox[0]
        x = (width - line_width) // 2
        draw.text((x + shadow_offset, y + shadow_offset), line, font=font, fill="black")
        draw.text((x, y), line, font=font, fill="white")
        y += line_height
    
    # Save the image with timestamp reflecting current date and time
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(ROOT_FOLDER, f"post_{timestamp}.png")
    image.save(output_path, "PNG")
    return output_path

# Step 4: Save Caption to Text File
def save_caption(caption, timestamp):
    caption_path = os.path.join(ROOT_FOLDER, f"caption_{timestamp}.txt")
    with open(caption_path, "w") as f:
        f.write(caption)
    return caption_path

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
            options.add_argument("--headless")
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
            
            # Step 2.2: Click the "Create" button to start a new post
            logger.info("Clicking Create button...")
            create_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "svg[aria-label='New post']"))
            )
            create_button.click()
            time.sleep(random.uniform(2, 3))
            
            # Step 2.3: Click "Post" to select the type of post
            logger.info("Clicking Post button...")
            post_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Post')] | //*[contains(@aria-label, 'Post')] | //*[contains(text(), 'Create a post')]"))
            )
            post_button.click()
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
    # Generate text and caption
    quote, caption = generate_motivational_content()
    print("Generated Quote:", quote)
    print("Generated Caption:", caption)
    
    # Generate image
    image = generate_aesthetic_image()
    
    # Merge text onto image
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = merge_text_on_image(image, quote)
    print("Image saved at:", image_path)
    
    # Save caption
    caption_path = save_caption(caption, timestamp)
    print("Caption saved at:", caption_path)
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