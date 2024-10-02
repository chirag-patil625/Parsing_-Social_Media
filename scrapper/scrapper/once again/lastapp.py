from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
import time
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

# Set up Chrome options
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")

# Initialize the Chrome WebDriver with the specified options
driver = webdriver.Chrome(options=chrome_options)

# Define X (formerly Twitter) URL and login credentials
x_url = "https://x.com/login"
username = "wisdomInBytes"
password = "chiragpatil625"

def x_login():
    driver.get(x_url)
    time.sleep(5)  # Initial delay

    try:
        username_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "text"))
        )
        username_field.send_keys(username)
        username_field.send_keys(Keys.RETURN)

        time.sleep(3)  # Wait for password field to appear

        password_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)
        
        time.sleep(10)  # Delay after login

        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//a[@aria-label='Profile']"))
            )
            print("Logged in successfully!")
            return True
        except:
            print("Login failed. Please check your credentials.")
            return False

    except Exception as e:
        print(f"Error occurred during login: {e}")
        return False

def capture_profile_screenshots():
    profile_url = f"https://x.com/{username}"
    driver.get(profile_url)
    time.sleep(10)  # Delay for profile loading

    if not os.path.exists('screenshots'):
        os.makedirs('screenshots')

    screenshots = []

    # Capture profile screenshot
    profile_screenshot = "screenshots/x_profile_screenshot.png"
    driver.save_screenshot(profile_screenshot)
    screenshots.append(profile_screenshot)
    print(f"Profile screenshot saved as {profile_screenshot}")

    # Capture all posts
    posts_screenshots = capture_all_posts()
    screenshots.extend(posts_screenshots)

    return screenshots

def capture_all_posts():
    posts_screenshots = []
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_pause_time = 3
    max_scrolls = 20
    max_retries = 3

    for i in range(max_scrolls):
        # Scroll down slowly
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)

        # Capture screenshot of visible posts
        screenshot_name = f"screenshots/x_posts_screenshot_{i + 1}.png"
        driver.save_screenshot(screenshot_name)
        posts_screenshots.append(screenshot_name)
        print(f"Posts screenshot saved as {screenshot_name}")

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("Reached the end of the page or no new posts loaded.")
            break
        last_height = new_height

        # Capture individual post screenshots
        for retry in range(max_retries):
            try:
                posts = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, '//article[@data-testid="tweet"]'))
                )
                for j, post in enumerate(posts, start=1):
                    try:
                        WebDriverWait(driver, 10).until(EC.visibility_of(post))
                        post_screenshot_name = f"screenshots/x_individual_post_{i+1}_{j}.png"
                        post.screenshot(post_screenshot_name)
                        posts_screenshots.append(post_screenshot_name)
                        print(f"Individual post screenshot saved as {post_screenshot_name}")
                    except (StaleElementReferenceException, TimeoutException):
                        print(f"Failed to capture screenshot for post {i+1}_{j}")
                        continue
                break  # If successful, break out of the retry loop
            except (StaleElementReferenceException, TimeoutException):
                if retry == max_retries - 1:
                    print(f"Failed to capture posts after {max_retries} attempts")
                else:
                    print(f"Retrying to capture posts (attempt {retry + 2})")
                    time.sleep(2)  # Wait before retrying

    return posts_screenshots
def create_pdf(images):
    pdf_file_name = "x_profile_and_posts_screenshots.pdf"
    c = canvas.Canvas(pdf_file_name, pagesize=letter)
    width, height = letter

    for image in images:
        if os.path.exists(image):
            img = Image.open(image)
            img_width, img_height = img.size
            aspect = img_height / float(img_width)

            # Resize image to fit the page
            if img_width > width:
                img_width = width
                img_height = img_width * aspect

            c.drawImage(image, 0, height - img_height, width=img_width, height=img_height)
            c.drawString(10, 30, os.path.basename(image))
            c.showPage()
        else:
            print(f"Image file not found: {image}")

    try:
        c.save()
        print(f"PDF created: {pdf_file_name}")
    except Exception as e:
        print(f"Error creating PDF: {e}")

# Main execution
if x_login():
    screenshots = capture_profile_screenshots()
    create_pdf(screenshots)
    print(f"Total screenshots captured: {len(screenshots)}")

# Close the browser
driver.quit()