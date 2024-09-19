import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from gpt4all import GPT4All

class LinkedInAutomation:
    def __init__(self):
        self.setup_driver()
        self.setup_gpt_model()

    def setup_driver(self):
        print("Setting up Chrome driver...")
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--log-level=3")  # Suppress most Chrome logs
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)
        print("Chrome driver set up successfully")

    def setup_gpt_model(self):
        print("Initializing GPT model...")
        self.gpt_model = GPT4All("orca-mini-3b-gguf2-q4_0.gguf")
        print("GPT model initialized successfully")

    def login_to_linkedin(self, email, password):
        print("Logging into LinkedIn...")
        self.driver.get("https://www.linkedin.com/login")
        try:
            email_field = self.wait.until(EC.presence_of_element_located((By.ID, "username")))
            password_field = self.wait.until(EC.presence_of_element_located((By.ID, "password")))
            submit_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
            
            email_field.send_keys(email)
            password_field.send_keys(password)
            submit_button.click()
            
            self.wait.until(EC.url_contains("feed"))
            print("Successfully logged into LinkedIn")
        except Exception as e:
            print(f"Failed to log in: {str(e)}")
            raise
        
    def scrape_feed(self):
        try:
            print("Navigating to LinkedIn feed...")
            self.driver.get("https://www.linkedin.com/feed/")
            
            print("Waiting for feed to load...")
            time.sleep(10)
            
            self.driver.execute_script("window.scrollTo(0, 1000)")
            time.sleep(5)
            
            print("Looking for posts...")
            posts = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".feed-shared-update-v2, .occludable-update")))
            
            print(f"Found {len(posts)} posts")
            
            topics = []
            for post in posts[:5]:
                try:
                    text = post.find_element(By.CSS_SELECTOR, ".feed-shared-update-v2__description-wrapper, .feed-shared-text").text
                    # Clean up the text
                    text = re.sub(r'\s+', ' ', text).strip()
                    if text:
                        topics.append(text)
                        print(f"Extracted text: {text[:100]}...")  # Print first 100 characters of each post
                except NoSuchElementException:
                    print("Couldn't extract text from a post, skipping...")
            
            return topics

        except TimeoutException:
            print("Timed out waiting for posts to load. LinkedIn might have changed their structure or the page didn't load properly.")
            print(f"Current URL: {self.driver.current_url}")
            print(f"Page source: {self.driver.page_source[:1000]}")  # Print first 1000 characters of page source
        except Exception as e:
            print(f"An error occurred while scraping the feed: {str(e)}")
        
        return []  # Return an empty list if we couldn't scrape any topics

    def create_content_from_feed(self):
        topics = self.scrape_feed()
        if not topics:
            print("No topics found in the feed.")
            return

        for topic in topics:
            prompt = f"Create a LinkedIn post about: {topic}"
            response = self.gpt_model.generate(prompt, max_tokens=200)
            print(f"Generated post:\n{response}\n")
    def close(self):
        if self.driver:
            self.driver.quit()

if __name__ == "__main__":
    try:
        linkedin_bot = LinkedInAutomation()
        
        # Add your LinkedIn credentials here
        email = "rajulucky400@gmail.com"
        password = "Rajesh@2847"
        linkedin_bot.login_to_linkedin(email, password)
        linkedin_bot.create_content_from_feed()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        print(traceback.format_exc())
    finally:
        if 'linkedin_bot' in locals():
            linkedin_bot.close()