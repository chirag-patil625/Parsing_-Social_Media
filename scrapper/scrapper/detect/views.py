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

def homepage(request):
    return render(request, 'home.html')

@csrf_exempt
def twitter(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        report_pdf = twitter_login_and_capture(username, password)

        if report_pdf:
            with open(report_pdf, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(report_pdf)}"'
                return response
        else:
            return HttpResponse("Login failed or report generation failed. Please try again.")

    return render(request, 'twitter.html')

def twitter_login_and_capture(username, password):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)
    twitter_url = "https://twitter.com/login"

    try:
        driver.get(twitter_url)
        time.sleep(5)  # Allow time for the page to load

        # Wait for username field and enter username
        username_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "text"))
        )
        username_field.send_keys(username)
        username_field.send_keys(Keys.RETURN)

        time.sleep(3)  # Wait for password field to appear

        # Wait for password field and enter password
        password_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)

        time.sleep(10)  # Delay after login

        # Check if logged in successfully
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//a[@aria-label='Profile']"))
            )
            print("Logged in successfully!")

            # Capture screenshots and generate PDF
            screenshots = []
            profile_screenshot = capture_twitter_profile(driver, username)
            if profile_screenshot:
                screenshots.append(profile_screenshot)

            posts_screenshots = capture_user_twitter_posts(driver, username)
            screenshots.extend(posts_screenshots)

            # Check if any screenshots were captured
            if not screenshots:
                print("No screenshots captured. Exiting.")
                return None

            # Generate PDF from all screenshots
            pdf_file = create_pdf_x(screenshots)
            return pdf_file

        except:
            print("Login failed. Please check your credentials.")
            return False

    except Exception as e:
        print(f"Error occurred during login: {e}")
        return False

    finally:
        driver.quit()



def capture_twitter_profile(driver, username):
    profile_url = f"https://x.com/{username}"
    driver.get(profile_url)
    time.sleep(5)  # Allow time for the profile to load

    if not os.path.exists('screenshots'):
        os.makedirs('screenshots')

    # Capture profile screenshot
    profile_screenshot = "screenshots/x_profile_screenshot.png"
    driver.save_screenshot(profile_screenshot)
    print(f"Profile screenshot saved as {profile_screenshot}")

    return profile_screenshot  # Return the path of the profile screenshot

def capture_user_twitter_posts(driver, username):
    posts = []

    # Navigate to the user's tweets
    driver.get(f"https://x.com/{username}/with_replies")
    time.sleep(5)  # Wait for tweets to load

    # Find all tweet elements (this may vary depending on the actual structure of the Twitter page)
    tweet_elements = driver.find_elements(By.XPATH, "//article[@role='article']")

    for i, tweet_element in enumerate(tweet_elements[:5]):  # Limit to the first 5 tweets
        if not os.path.exists('screenshots'):
            os.makedirs('screenshots')

        # Save each tweet as a screenshot
        tweet_screenshot = f"screenshots/x_tweet_{i+1}.png"
        tweet_element.screenshot(tweet_screenshot)
        print(f"Tweet screenshot saved as {tweet_screenshot}")
        posts.append(tweet_screenshot)

    return posts

def create_pdf_x(images):
    pdf_file = "twitter_report.pdf"
    c = canvas.Canvas(pdf_file, pagesize=letter)
    width, height = letter

    for image in images:
        # Set the image size and position
        c.drawImage(image, 0, 0, width=width, height=height, preserveAspectRatio=True)
        c.showPage()  # Add a new page for each image

    c.save()
    print(f"PDF report saved as {pdf_file}")
    return pdf_file

