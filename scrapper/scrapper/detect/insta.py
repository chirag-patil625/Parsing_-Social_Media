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
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

@csrf_exempt
def instagram(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        report_pdf = instagram_login_and_capture(username, password)

        if report_pdf:
            with open(report_pdf, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(report_pdf)}"'
                return response
        else:
            return HttpResponse("Login failed or report generation failed. Please try again.")

    return render(request, 'instagram.html')

def instagram_login_and_capture(username, password):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)
    instagram_url = "https://www.instagram.com/accounts/login/"

    try:
        driver.get(instagram_url)
        time.sleep(5)  # Allow time for the page to load

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )

        username_input = driver.find_element(By.NAME, "username")
        password_input = driver.find_element(By.NAME, "password")

        username_input.send_keys(username)
        password_input.send_keys(password)

        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()

        time.sleep(10)  # Wait for login process

        # Check if logged in successfully
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/explore/')]"))
            )
            print("Logged in successfully!")
        except Exception as login_error:
            print(f"Login failed. Please check your credentials. Error: {login_error}")
            return None

        # Capture screenshots and generate PDF
        screenshots = []
        profile_screenshot = capture_instagram_profile(driver, username)
        if profile_screenshot:
            screenshots.append(profile_screenshot)

        posts_screenshots = capture_instagram_posts(driver, username)
        screenshots.extend(posts_screenshots)

        # Check if any screenshots were captured
        if not screenshots:
            print("No screenshots captured. Exiting.")
            return None

        # Generate PDF from all screenshots
        pdf_file = create_pdf(screenshots)
        return pdf_file

    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        driver.quit()

def capture_instagram_profile(driver, username):
    profile_url = f"https://www.instagram.com/{username}/"
    driver.get(profile_url)
    time.sleep(5)  # Allow time for the profile to load

    if not os.path.exists('screenshots'):
        os.makedirs('screenshots')

    # Capture the full profile screenshot
    driver.save_screenshot("screenshots/temp_full_screenshot.png")
    full_profile_screenshot = "screenshots/temp_full_screenshot.png"
    return full_profile_screenshot
    # try:
    #     # Attempt to locate the profile picture element
    #     profile_pic_element = WebDriverWait(driver, 20).until(
    #         EC.presence_of_element_located((By.XPATH, "//img[contains(@class, '_aadp')]"))
    #     )
    #     location = profile_pic_element.location
    #     size = profile_pic_element.size
        
    #     # Open the full screenshot to crop if needed
    #     im = Image.open("screenshots/temp_full_screenshot.png")
    #     left = location['x']
    #     top = location['y']
    #     right = left + size['width']
    #     bottom = top + size['height']

    #     # Save the cropped profile picture if required
    #     profile_screenshot = "screenshots/profile_picture_screenshot.png"
    #     im_cropped = im.crop((left, top, right, bottom))
    #     im_cropped.save(profile_screenshot)
        
    #     print(f"Profile picture screenshot saved as {profile_screenshot}")

    #     # Save the full screenshot of the profile page
    #     full_profile_screenshot = "screenshots/instagram_profile_screenshot.png"
    #     im.save(full_profile_screenshot)
    #     print(f"Full profile screenshot saved as {full_profile_screenshot}")

    #     return full_profile_screenshot  # Return the path of the full profile screenshot
    
    # except Exception as e:
    #     print(f"Error capturing profile: {e}")
    #     return None  # Return None if there is an error


def capture_instagram_posts(driver, username):
    posts = []
    time.sleep(2)  # Wait for posts to load

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

def create_pdf(images):
    pdf_file = "instagram_report.pdf"
    c = canvas.Canvas(pdf_file, pagesize=letter)
    width, height = letter

    for image in images:
        c.drawImage(image, 0, 0, width=width, height=height, preserveAspectRatio=True)
        c.showPage()  # Add a new page for each image

    c.save()
    print(f"PDF report saved as {pdf_file}")
    return pdf_file