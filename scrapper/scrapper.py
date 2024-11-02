import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth  

class WebScraper:
    # setting up the necessary config for the webscrapper
    def __init__(self, download_path,executable_path="./chromedriver.exe"):
        self.options = Options()
        self.service = Service(executable_path=executable_path)
        self.download_path = download_path
        self.options.add_argument("start-maximized")
        self.options.add_argument("--headless")  # Comment out for visible browsing
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        
        # Initialize the Chrome driver
        self.driver = webdriver.Chrome(options=self.options, service=self.service)
        
        # Apply stealth mode
        stealth(self.driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )
    # the website jiji requires you to scroll down inorder to 
    # bring out another item
    def scroll_down(self, duration):
        end_time = time.time() + duration
        while time.time() < end_time:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)  # Wait for a second to allow new items to load

    def navigate_to(self, url):
        self.driver.get(url)
        self.driver.implicitly_wait(5)  # Adjust wait time as necessary

    # function that will scrape the data and store it inside a csv file
    def scrape_data(self, class_name, item_name):
        elements = self.driver.find_elements(By.CLASS_NAME, class_name)
        output_file=f'{self.download_path}/data.csv'
        with open(output_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Item Name','Price', "Description","Location","Full"])  # Adjust column headers as needed
            
            for element in elements:
                description = element.text  # Replace with the method to get the desired text
                # Split at the first occurrence of \n
                first_split = description.split('\n', 1)

                # If there is a second part, split that at the last occurrence of \n
                if len(first_split) > 1:
                    last_split = first_split[1].rsplit('\n', 1)
                else:
                    last_split = ["", ""]
                    
                first_part = first_split[0]
                middle_part = last_split[0]
                last_part = last_split[1]
                joint = f"This item with name {item_name} with description '{middle_part}' has a price of {first_part} and is located at {last_part}."
                cleaned_text = joint.replace('\n', ' ')
                writer.writerow([item_name,first_part, middle_part,last_part,cleaned_text])  # Adjust as needed
    
    def close(self):
        self.driver.quit()



