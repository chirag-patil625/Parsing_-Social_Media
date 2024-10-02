from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
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

# Define Instagram URL and login credentials
instagram_url = "https://www.instagram.com/accounts/login/"
username = "tanmayy._9"  # Replace with your Instagram username
password = "tanmaypatil3303"  # Replace with your Instagram password

def instagram_login():
    driver.get(instagram_url)
    time.sleep(5)  # Increased initial delay

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )

        username_input = driver.find_element(By.NAME, "username")
        password_input = driver.find_element(By.NAME, "password")

        username_input.send_keys(username)
        password_input.send_keys(password)

        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        
        time.sleep(10)  # Increased delay after login

        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/explore/')]"))
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
    profile_url = f"https://www.instagram.com/{username}/"
    driver.get(profile_url)
    time.sleep(10)  # Increased delay for profile loading

    if not os.path.exists('screenshots'):
        os.makedirs('screenshots')

    screenshots = []

    # Capture profile screenshot
    profile_screenshot = "screenshots/profile_screenshot.png"
    driver.save_screenshot(profile_screenshot)
    screenshots.append(profile_screenshot)
    print(f"Profile screenshot saved as {profile_screenshot}")

    # Capture all posts
    posts_screenshots = capture_all_posts()
    screenshots.extend(posts_screenshots)

    # Capture and crop profile picture
    profile_pic_screenshot = capture_profile_picture()
    if profile_pic_screenshot:
        screenshots.append(profile_pic_screenshot)

    return screenshots

def capture_all_posts():
    posts_screenshots = []
    last_height = driver.execute_script("return document.body.scrollHeight")
    max_scrolls = 5  # Limit the number of scrolls to 5
    for i in range(max_scrolls):
        # Scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Reduced delay for loading posts
        # Capture screenshot
        screenshot_name = f"screenshots/posts_screenshot_{i + 1}.png"
        driver.save_screenshot(screenshot_name)
        posts_screenshots.append(screenshot_name)
        print(f"Posts screenshot saved as {screenshot_name}")
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    return posts_screenshots

def capture_profile_picture():
    try:
        profile_pic_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//img[contains(@class, '_aadp')]"))
        )
        location = profile_pic_element.location
        size = profile_pic_element.size
        driver.save_screenshot("screenshots/temp_full_screenshot.png")

        im = Image.open("screenshots/temp_full_screenshot.png")
        left = location['x']
        top = location['y']
        right = left + size['width']
        bottom = top + size['height']

        im_cropped = im.crop((left, top, right, bottom))
        profile_pic_screenshot = "screenshots/profile_picture_screenshot.png"
        im_cropped.save(profile_pic_screenshot)
        print(f"Cropped profile picture screenshot saved as {profile_pic_screenshot}")
        return profile_pic_screenshot
    except Exception as e:
        print(f"Error capturing profile picture: {e}")
        return None

def create_pdf(images):
    pdf_file_name = "instagram_profile_screenshots.pdf"
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
if instagram_login():
    screenshots = capture_profile_screenshots()
    create_pdf(screenshots)
    print(f"Total screenshots captured: {len(screenshots)}")

# Close the browser
driver.quit()