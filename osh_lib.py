from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException
import time
import datetime
import os
import html
import config
from bs4 import BeautifulSoup

class OpenSupplyHubScraper:
    def __init__(self, keyword, countrycode=0):
        self.keyword = keyword
        self.countrycode = countrycode
        self.script_directory = os.path.dirname(os.path.abspath(__file__))
        self.chrome_options = self.setup_chrome_options()
        self.driver = self.setup_driver()
        self.wait = WebDriverWait(self.driver, 10)
        self.url = 'https://opensupplyhub.org/auth/login'

    def setup_chrome_options(self):
        chrome_options = Options()
        chrome_options.add_experimental_option("prefs", {
            "detach": True,
            "download.default_directory": self.script_directory,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        })
        return chrome_options

    def setup_driver(self):
        return webdriver.Chrome(options=self.chrome_options)

    def login(self):
        self.driver.get(self.url)
        page_source = self.driver.page_source
        with open("page_source.html", "w", encoding="utf-8") as file:
            file.write(html.unescape(page_source))

        elements = config.elements

        for element in elements:
            try:
                if 'id' in element:
                    WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.ID, element['id']))
                    ).send_keys(element['value'])
                    print(element['message'])
                elif 'xpath' in element:
                    if element.get('action') == 'click':
                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, element['xpath']))
                        ).click()
                        print(element['message'])
            except Exception as e:
                print(f"ERROR: {e}")

    def list_populator(self):
        try:
            WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.XPATH, "//body")))
            xpath_check = WebDriverWait(self.driver, 15).until(EC.presence_of_all_elements_located((By.ID, 'FACILITIES')))
            self.driver.find_element(By.ID, 'FACILITIES').send_keys(self.keyword)
            if self.countrycode != 0:
                self.driver.find_elements(By.XPATH, "//*[starts-with(@class, 'select__value-container')]").click()
                dropdown_check = WebDriverWait(self.driver, 15).until(EC.presence_of_all_elements_located((By.ID, 'react-select-5-option-249')))
                self.driver.find_element(By.ID, f'react-select-5-option-{self.countrycode}').click()
            search_button_check = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.XPATH, '//main/div/div[1]/div/div[2]/div[1]/button'))).click()
            download_button_check = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.XPATH, '//main/div/div[2]/div[2]/div/div/button'))).click()
                   # Get the current date
            current_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

            # Find the "CSV" option element and modify the link
            csv_option = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//div[@id='download-menu']/div[2]/ul/li"))
            )
            original_link = csv_option.get_attribute("href")
            print(original_link)
            modified_link = f"{original_link}&filename=facilities_{current_date}.csv"
            print(modified_link)
            self.driver.execute_script(f"arguments[0].setAttribute('href', '{modified_link}')", csv_option)

            # Click the modified "CSV" option
            csv_option.click()

            time.sleep(5)
        except:
            print("not found")

    def csv_reader(self):
        # Wait for the file to download
        timeout = 60  # Adjust timeout as needed
        start_time = time.time()
        while not any(fname.endswith('.csv') for fname in os.listdir(self.script_directory)):
            if time.time() - start_time > timeout:
                print("Timeout occurred while waiting for the file to download.")
                break
            time.sleep(1)

        # Read the downloaded file
        # Replace "example.csv" with your actual file name
        downloaded_file_path = os.path.join(self.script_directory, "facilities.csv")
        if os.path.exists(downloaded_file_path):
            with open(downloaded_file_path, 'r') as file:
                csv_content = file.read()
            print("CSV file content:")
            print(csv_content)
        else:
            print("File not found:", downloaded_file_path)

    def quit_driver(self):
        self.driver.quit()

if __name__ == "__main__":
    print("Library file cant be run individually")