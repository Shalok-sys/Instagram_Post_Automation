# Instagram Motivational Post Automation

This project automatically generates inspirational quote images with aesthetically pleasing backgrounds and publishes them to Instagram using Selenium.

---

## 🚀 Features

- ✅ **Auto-generate motivational quotes** with captions using [Pollinations.AI](https://pollinations.ai/)
- ✅ **Create aesthetic, watermark-free images** using AI-generated art and overlay quotes with custom fonts
- ✅ **Automatically log in to Instagram** and publish the latest generated image + caption
- ✅ **Handles Instagram UI changes** gracefully with multiple selectors and retry logic
- ✅ **Logs events** and failures using Python's logging module
- ✅ **Saves posts locally** with timestamped naming (`post_YYYYMMDD_HHMMSS.png` + caption)

---

## 🧠 How It Works

### Step 1: Generate Quote + Caption

- A random quote theme and historical figure is selected
- Pollinations.AI generates a quote and caption with hashtags
- The quote and caption are saved

### Step 2: Generate Image

- A random visual theme is used to query Pollinations.AI
- Watermark is cropped and the image is resized to 1080x1080
- The quote is overlayed using `Pillow` with custom font logic

### Step 3: Save Assets

- The image is saved as `post_TIMESTAMP.png`
- The caption is saved as `caption_TIMESTAMP.txt`

### Step 4: Upload to Instagram

- Uses Selenium with headless Chrome
- Logs into Instagram using environment variables
- Uploads image, fills caption, and posts it
- Handles "Save login" and "Turn on notifications" prompts
- Retries if upload fails

---

## 🛠 Requirements

Install required Python libraries:

```bash
pip install -r requirements.txt
```

## 🔐 Environment Variables

Create a `.env` file or export these variables before running:

```
INSTA_USERNAME=your_instagram_username
INSTA_PASSWORD=your_instagram_password
```

## ▶️ Usage

Run the automation:

```
python ultimate.py
# Generates Image wth caption.
python main.py
# Runs the python script to catch the caption and image from the local repository and upload them to Instagram.
```

## 🧪 Troubleshooting

- Ensure **`chromedriver.exe`** matches your installed Chrome version
- Avoid frequent posting to prevent Instagram bans
- Use **non-headless mode** (remove `--headless`) to debug UI interactions
- Make sure `Montserrat-SemiBold.ttf` is in the same directory

## 🧠 Credits

- [Pollinations.AI](https://pollinations.ai/) for text and image generation
- Selenium WebDriver for browser automation
- Python Pillow for image processing

## 📅 Possible Improvements

- [ ] Schedule daily runs with `cron` or `Task Scheduler`
- [ ] Store post history in SQLite or JSON
- [ ] Multi-account rotation support
- [ ] Integrate the generation and publising process.
