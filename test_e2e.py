"""
Simple end-to-end test to verify the Flask app displays the expected text in Chrome.
"""
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_app_displays_hello_world():
    """Test that the app shows 'Hello, World! This is a simple Python Flask application running in Docker.' text."""
    
    # Get the app URL from environment or use default
    app_url = os.environ.get('APP_URL', 'http://localhost:8888')
    
    # Configure Chrome options
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    # Set Chrome binary location if found
    chrome_binary_paths = [
        '/usr/bin/google-chrome',
        '/opt/chrome/chrome',
        '/opt/chrome/google-chrome'
    ]
    for path in chrome_binary_paths:
        if os.path.exists(path):
            options.binary_location = path
            break
    
    # Set chromedriver path
    chromedriver_paths = [
        '/usr/bin/chromedriver',
        '/usr/local/bin/chromedriver',
        '/usr/src/app/node_modules/chromedriver/bin/chromedriver'
    ]
    
    chromedriver_path = None
    for path in chromedriver_paths:
        if os.path.exists(path):
            chromedriver_path = path
            break
    
    # Fallback to WebDriver Manager if chromedriver not found
    if not chromedriver_path:
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            chromedriver_path = ChromeDriverManager().install()
        except Exception:
            raise RuntimeError("Chromedriver not found and WebDriver Manager failed")
    
    # Create service and driver
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        # Navigate to the app
        driver.get(app_url)
        
        # Wait for the page to load
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Get the page text and normalize whitespace
        page_text = driver.find_element(By.TAG_NAME, "body").text
        normalized_page_text = ' '.join(page_text.split())
        
        # Expected text to check
        expected_text = "Hello, World! This is a simple Python Flask application running in Docker."
        
        # Verify the text is present
        assert expected_text in normalized_page_text, f"Expected text '{expected_text}' not found. Normalized page text: {normalized_page_text}"
        
    finally:
        driver.quit()


if __name__ == '__main__':
    test_app_displays_hello_world()
    print("E2E test completed successfully!")
