from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from parsel import Selector
import time
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

def initialize_driver():
    options = webdriver.ChromeOptions()

    # To make browser stay open
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=options)
    
    return driver

def close_driver(driver):
    # driver.quit()
    driver.close()
    
def navigate_driver_to_url(driver, url):
    driver.get(url)


def navigate_to_reviews_tab(driver):
    reviews_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label*=Reviews]")
    aria_selected = reviews_button.get_attribute("aria-selected")
    
    if aria_selected == "false":
        reviews_button.click()
        time.sleep(3)
        
    else:
        return
    
# Function to click the "More" button to expand on a review
def expand_review(driver):
    more_buttons = driver.find_elements(By.CSS_SELECTOR, ".w8nwRe.kyuRq")
    
    for button in more_buttons:
    # In the cases of the class corresponding to the wrong element, an exception is needed
        try:
            # more_button = driver.find_element(By.CSS_SELECTOR, ".w8nwRe.kyuRq")
            button.click()
            time.sleep(1)
            
        except:
            pass


def scroll_down(driver):
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

def scrape_reviews(driver):
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.jftiEf.fontBodyMedium')))

    # retrieves HTML source code of current webpage loaded in WebDriver instance
    page_content = driver.page_source

    # creates a Selector object, which allows us to extract data from HTML using XPATH or CSS selectors
    response = Selector(text=page_content)

    reviews_list = []
    meal_types = ["Breakfast", "Lunch", "Dinner"]
    
    #ce = []
    #c = []
    
    # for element in response.xpath('//div[@data-review-id]'):
    for element in response.css('.jftiEf.fontBodyMedium'):
        
        # CSS selector is used to target div element with class name 'd4r55' and extracts its corresponding text
        # get(default='') retrieves the first matching element's text or returns empty string if no match
        name = element.css('div.d4r55::text').get(default='').strip()
        
        # Selects span element of class name 'kvMYJc' and retrieves the value of the aria-label attribute, and replaces ' stars' with empty string
        aria_label = element.css('span.kvMYJc::attr(aria-label)').get(default='').strip()
        rating = re.sub(r'\bstars?\b', '', aria_label).strip()
        # rating = element.css('span.kvMYJc::attr(aria-label)').get(default='').replace(' stars', '').strip()
        
        food_rating = None
        service_rating = None
        atmosphere_rating = None
        meal_type = None
        
        # HAVE TO MAKE SURE REVIEW IS EXPANDED FOR SPAN TO BE DETECTED
        for span_element in element.css('span.RfDO5c'):
            category = span_element.css('b::text').get(default='').strip()
            category_rating = span_element.css('span::text').get(default='').strip()
            
            #c.append(category_rating)
            #ce.append(category)
            
            #Meal type and actual type can be grabbed though category_rating code
            if category_rating.isdigit():
                if category == "Food:":
                    food_rating = category_rating
                elif category == "Service:":
                    service_rating = category_rating
                elif category == "Atmosphere:":
                    atmosphere_rating = category_rating
            
            else:
                if category_rating in meal_types:
                    meal_type = category_rating

            
        
        body = element.css('span.wiI7pd::text').get(default='').strip()

        name_exists = False
        for review in reviews_list:
            if review['name'] == name:
                name_exists = True
                break
            
        # "if not" checks if the variable is False. If it is false, execute 
        if not name_exists:
            reviews_list.append({'name': name, 'rating': rating, 'body': body, 'meal_type' : meal_type, 'food_rating': food_rating, 'service_rating': service_rating, 'atmosphere_rating': atmosphere_rating})
    #print(c)
    #print('\n', ce)
    return reviews_list

def print_reviews(reviews_list):
    for review in reviews_list:
        # Encode the name to UTF-8 and decode it back to ensure correct representation (aka keeping the names the way they were originally represented)
        name = review['name'].encode('utf-8', errors='ignore').decode('utf-8')

        print("{")
        
        print("\tName:", name)
        print("\tRating:", review['rating']),
        print("\tMeal type:", review['meal_type']),
        print("\tFood:", review['food_rating']),
        print("\tService:", review['service_rating']),
        print("\tAtmosphere:", review['atmosphere_rating']),
        print("\tBody:"),

        # Process each line of the review body
        for line in review['body'].split('\n'):
            # Check if the line contains any non-ASCII characters
            if any(ord(char) > 127 for char in line):
                # If there are non-ASCII characters, encode with UTF-8
                encoded_line = line.strip().encode('utf-8', errors='ignore')
            else:
                encoded_line = line.strip().encode('utf-8')

            decoded_line = encoded_line.decode('utf-8')
            print("\t", decoded_line)

        print("}")
        
def main():
    driver = initialize_driver()
    
    # Reviews url
    url = 'https://www.google.com/maps/place/Hudson+Buffet/@41.5286056,-73.8972371,17z/data=!4m8!3m7!1s0x89dd36fc398c602f:0x929fb2bcf9639a91!8m2!3d41.5286056!4d-73.8946622!9m1!1b1!16s%2Fg%2F1tdxlwgg?entry=ttu'
    
    # Overview url
    #url = "https://www.google.com/maps/place/Hudson+Buffet/@41.5286096,-73.8972371,17z/data=!3m1!4b1!4m6!3m5!1s0x89dd36fc398c602f:0x929fb2bcf9639a91!8m2!3d41.5286056!4d-73.8946622!16s%2Fg%2F1tdxlwgg?entry=ttu"
    
    navigate_driver_to_url(driver, url)
    #navigate_to_reviews_tab(driver)
    
    #scroll_down(driver)
    expand_review(driver)
    reviews_dict = scrape_reviews(driver)
    
    print_reviews(reviews_dict)
    
    close_driver(driver)
    
if __name__ == "__main__":
    main()
    