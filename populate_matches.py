from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Initialize the Chrome driver
driver = webdriver.Chrome()

# Open the web page
driver.get("https://dstv.stream/livetv/play/0d14b71e-536e-4918-8482-f2609e89d9aa")  # Replace with the actual URL

# Wait until the element is present
wait = WebDriverWait(driver, 20)

try:
    # Example: Wait for the iframe to be available and switch to it if necessary
    iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe_selector")))
    driver.switch_to.frame(iframe)

    # Wait for the element containing the video URL
    element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "css_selector_for_video_url")))

    # Get the video URL
    video_url = element.get_attribute("src")
    print(f"Video URL: {video_url}")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()


