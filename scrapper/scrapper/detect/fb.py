from django.shortcuts import render
from django.http import HttpResponse
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import time
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def facebook(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        report_pdf = facebook_login_and_capture(username, password)

        if report_pdf:
            with open(report_pdf, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(report_pdf)}"'
                return response
        else:
            return HttpResponse("Login failed or report generation failed. Please try again.")

    return render(request, 'facebook.html')

def facebook_login_and_capture(username, password):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)
    facebook_url = "https://www.facebook.com/"

    try:
        driver.get(facebook_url)
        time.sleep(5)  # Allow time for the page to load

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "pass"))
        )

        email_input = driver.find_element(By.NAME, "email")
        password_input = driver.find_element(By.NAME, "pass")

        email_input.send_keys(username)
        password_input.send_keys(password)

        login_button = driver.find_element(By.NAME, "login")
        login_button.click()

        time.sleep(10)  # Wait for login process

        # Check if logged in successfully
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/friends/')]"))
            )
            print("Logged in successfully!")
        except Exception as login_error:
            print(f"Login failed. Please check your credentials. Error: {login_error}")
            return None

        # Capture screenshots and generate PDF
        screenshots = []
        profile_screenshot = capture_facebook_profile_screenshots(driver)
        if profile_screenshot:
            screenshots.append(profile_screenshot)

        posts_screenshots = capture_facebook_all_posts(driver)
        screenshots.extend(posts_screenshots)

        # Check if any screenshots were captured
        if not screenshots:
            print("No screenshots captured. Exiting.")
            return None

        # Generate PDF from all screenshots
        pdf_file = create_pdf_facebook(screenshots)
        return pdf_file

    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        driver.quit()

def dismiss_notifications(driver):
    try:
        # Wait for the notifications element to be present
        time.sleep(2)  # Wait to ensure the page is fully loaded
        notification_button = driver.find_element(By.XPATH, "//div[contains(@aria-label, 'Notifications')]")
        notification_button.click()  # Click to open notifications

        # Click the 'Close' button if it exists
        close_button = driver.find_element(By.XPATH, "//div[@role='dialog']//div[@aria-label='Close']")
        close_button.click()
        print("Notifications dismissed.")
    except Exception as e:
        print(f"Could not dismiss notifications: {e}")

def capture_facebook_profile_screenshots(driver):
    profile_url = "https://www.facebook.com/me/"
    driver.get(profile_url)
    time.sleep(5)  # Allow time for the profile to load

    if not os.path.exists('screenshots'):
        os.makedirs('screenshots')

    # Capture profile screenshot
    profile_screenshot = "screenshots/facebook_profile_screenshot.png"
    driver.save_screenshot(profile_screenshot)
    print(f"Profile screenshot captured: {profile_screenshot}")
    return profile_screenshot

def capture_facebook_all_posts(driver):
    # Navigate to the Facebook activity page
    driver.get("https://www.facebook.com/me/allactivity")
    time.sleep(2)  # Allow time for the posts to load

    dismiss_notifications(driver)  # Call the function to dismiss notifications
    
    # Check for screenshots directory
    if not os.path.exists('screenshots'):
        os.makedirs('screenshots')

    last_height = driver.execute_script("return document.body.scrollHeight")
    max_scrolls = 5  # Limit the number of scrolls to 5
    posts_screenshots = []
    for i in range(max_scrolls):
        # Scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Reduced delay for loading posts
        # Capture screenshot
        screenshot_name = f"screenshots/facebook_posts_screenshot_{i + 1}.png"
        driver.save_screenshot(screenshot_name)
        posts_screenshots.append(screenshot_name)
        print(f"Posts screenshot saved as {screenshot_name}")
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    return posts_screenshots

def create_pdf_facebook(images):
    pdf_file = "facebook_report.pdf"
    c = canvas.Canvas(pdf_file, pagesize=letter)
    width, height = letter

    for image in images:
        # Set the image size and position
        c.drawImage(image, 0, 0, width=width, height=height, preserveAspectRatio=True)
        c.showPage()  # Add a new page for each image
    c.save()
    print(f"PDF report saved as {pdf_file}")
    return pdf_file
