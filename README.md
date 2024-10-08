# Social Media Data Parsing Tool

## Problem Statement

### Description
During investigations, examining the social media accounts of suspects can be a daunting task. When social media accounts are opened for examination or to create Panchnamas, it would be beneficial to have a tool that can automatically parse the data. This tool should provide screenshots of various elements, including:

- Posts
- Messages
- Timelines
- Friend lists
- Following and followers
- Account information

This automation helps eliminate human error during the process and facilitates a thorough review of the data found on social media accounts. The tool should also offer separate options for popular social media platforms like Facebook, Twitter, Instagram, Telegram, WhatsApp, and Google accounts. 

In many instances, social media accounts may not open on desktops even when the correct credentials are provided, necessitating the use of a dummy Android phone. Therefore, having two separate versions of this tool (Android and Windows) would be immensely helpful.

## Approach

To address the problem statement, the following steps were taken:

1. **Gathered Information**: Conducted extensive research on the parsing of social media feeds and the specific requirements of the tool.
  
2. **Group Planning**: Collaborated with team members to outline the project's scope, requirements, and functionalities.

3. **Web Scraping**: Developed web scraping capabilities for multiple social media platforms (Instagram, Facebook, X) using Python and Selenium.

4. **Backend Development**: Built a robust backend using Django to handle the web scraping logic and data management.

5. **Platform-Specific Applications**: Created individual applications tailored for each social media platform (Instagram, Facebook, X) to extract necessary data.

6. **Integration**: Integrated all individual applications into a single backend to streamline data extraction processes.

7. **Mobile and Web Applications**: Developed mobile applications using React Native for Android and web applications using Python, HTML, CSS, and Django.

8. **Testing**: Conducted tests on the social media accounts of users (Instagram, Facebook, etc.) to ensure functionality and data accuracy.

9. **Model Improvement**: Iteratively improved the model based on feedback and testing outcomes.

10. **Sentiment Analysis Implementation**: Attempted to implement sentiment analysis to gain insights from user messages and posts.

11. **Future Improvements**: Planned for future enhancements to expand functionalities and improve performance.

## Installation

### Prerequisites

- Python 3.x
- Node.js (for React Native development)
- A modern web browser (for web application)

### Setup Environment

1. **Clone the Repository**:
   ```bash
   git clone <repository_url>
   cd <repository_directory>

2. **Set Up Virtual Environment:**
    ```bash
      python -m venv venv
      venv\Scripts\activate  

3. **Install Dependencies:**
- For the Django backend:
   ```bash
   pip install -r requirements.txt

- **For React Native development:**
   ```bash
   npm install

## Features

- Multi-Platform Support: Separate versions for Android and Windows to accommodate various use cases.

- Data Extraction: Automatically extracts and screenshots user profile photos, messages, posts, and account details.

- Document Generation: Compiles screenshots into a well-structured PDF document for easy review.

- User Interface: Intuitive UI for both mobile and web applications, allowing examiners to specify which data to capture.


### Screenshots of Features

- Example of data extraction from a user's profile.

- Example of a PDF document generated with screenshots.
(uploaded in Repository)


### Future Implementation

- Natural Language Processing (NLP): Future versions of the tool may incorporate NLP to analyze text data for context and insights.

- Optical Character Recognition (OCR): Implement OCR capabilities to extract text from images for further analysis.


### Contributing
- Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change. Please ensure that tests are updated as necessary.

### Code Example

- Here’s a list of libaraies used that demonstrates how to take scrolling screenshots of WhatsApp chats using Selenium:

   ```bash
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


# Contributing
- Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change. Please ensure that tests are updated as necessary.

# License
- This project is licensed under the MIT License. For more details, see MIT License.

```csharp
You can download this README file using the link below:

[Download README.md](sandbox:/mnt/data/Social_Media_Data_Parsing_Tool_README.md)
