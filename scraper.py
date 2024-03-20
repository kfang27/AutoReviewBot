from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from parsel import Selector
import time

options = webdriver.ChromeOptions()

# To make browser stay open
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=options)

url = 'https://www.google.com/maps/place/Hudson+Buffet/@41.5286056,-73.8972371,17z/data=!4m8!3m7!1s0x89dd36fc398c602f:0x929fb2bcf9639a91!8m2!3d41.5286056!4d-73.8946622!9m1!1b1!16s%2Fg%2F1tdxlwgg?entry=ttu'

driver.get(url)
   
# Function to click the "More" button to expand on a review
def expand_review():
    more_buttons = driver.find_elements(By.CSS_SELECTOR, ".w8nwRe.kyuRq")
    
    for button in more_buttons:
    # In the cases of the class corresponding to the wrong element, an exception is needed
        try:
            # more_button = driver.find_element(By.CSS_SELECTOR, ".w8nwRe.kyuRq")
            button.click()
            time.sleep(1)
            
        except:
            pass


def scroll_down():
    total_reviews_element = driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[2]/div/div[2]/div[3]')
    
    text_from_element = total_reviews_element.text
    total_reviews = int(text_from_element.split()[0])
    
    review_section = driver.find_element(By.CSS_SELECTOR, '.m6QErb.DxyBCb.kA9KIf.dS8AEf')
    
    while True:
        review_section.send_keys(Keys.END)
        time.sleep(1)
        
        # the CSS selector here is the actual container class for each review
        list_of_loaded_reviews = driver.find_elements(By.CSS_SELECTOR, '.jftiEf.fontBodyMedium')
        current_loaded_reviews = len(list_of_loaded_reviews)
        
        if current_loaded_reviews >= total_reviews:
            break
    
    print(total_reviews)
    print(current_loaded_reviews)

scroll_down()
     
# expand_review()
WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.jftiEf.fontBodyMedium')))

# retrieves HTML source code of current webpage loaded in WebDriver instance
page_content = driver.page_source

# creates a Selector object, which allows us to extract data from HTML using XPATH or CSS selectors
response = Selector(text=page_content)

results = []

# for element in response.xpath('//div[@data-review-id]'):
for element in response.css('.jftiEf.fontBodyMedium'):
    # expand_review()
    
    # CSS selector is used to target div element with class name 'd4r55' and extracts its corresponding text
    # get(default='') retrieves the first matching element's text or returns empty string if no match
    name = element.css('div.d4r55::text').get(default='').strip()
    
    # Selects span element of class name 'kvMYJc' and retrieves the value of the aria-label attribute, and replaces ' stars' with empty string
    rating = element.css('span.kvMYJc::attr(aria-label)').get(default='').replace(' stars', '').strip()
    body = element.css('span.wiI7pd::text').get(default='').strip()

    name_exists = False
    for review in results:
        if review['name'] == name:
            name_exists = True
            break
        
    # "if not" checks if the variable is False. If it is false, execute 
    if not name_exists:
        results.append({'name': name, 'rating': rating, 'body': body})

#driver.close()

for review in results:
    print(
        "{",
        "\n\t" + "Name:", review['name'],
        "\n\t" + "Rating:", review['rating'],
        "\n\t" + "Body:"
    )

    for line in review['body'].split('\n'):
            # Check if the line contains any non-ASCII characters
        if any(ord(char) > 127 for char in line):
            # If there are non-ASCII characters, encode with 'ascii' encoding and ignore errors
            encoded_line = line.strip().encode('ascii', errors='ignore')
            decoded_line = encoded_line.decode('ascii')
        else:
            # If there are no non-ASCII characters, proceed as before
            encoded_line = line.strip().encode('utf-8', errors='ignore')
            decoded_line = encoded_line.decode('utf-8')
        print("\t", decoded_line)
    print("},")

