import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium_stealth import stealth

# Create driver
driver = webdriver.Chrome()
stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True)
url = "https://www.skyscanner.com/transport/flights-from/cdg/230610/230630/?adultsv2=1&cabinclass=economy&childrenv2"
driver.get(url)

time.sleep(100)
chain = ActionChains(driver)
button = driver.find_element(By.XPATH, "//button[text()='OK']")
chain.move_to_element(button).click().perform()
time.sleep(60)

# Get all country destinations
countries = driver.find_elements(By.CLASS_NAME, 'browse-list-category')

def collect_destination_details(self, index):
    destination = self.driver.execute_script(f'''
                return document.
                    getElementsByClassName('browse-list-category open')[0].
                    getElementsByClassName('browse-data-entry')[{index}]
                ''')

    # Get destination name
    try:
        destination_name = destination.find_element(By.TAG_NAME, 'h3').text

        # Get flight link
        flight_link = destination.find_element(By.CLASS_NAME, 'flightLink').get_attribute('href')

        # Get hotel link
        hotel_link = destination.find_element(By.CLASS_NAME, 'hotelLink').get_attribute('href')

        # Get Prices
        prices = destination.find_elements(By.CLASS_NAME, 'price')
        flight_price = re.sub("[^0-9]", "", prices[0].text)
        hotel_price = re.sub("[^0-9]", "", prices[1].text)

        result = {'destination': destination_name,
                'flight_link': flight_link,
                'hotel_link': hotel_link,
                'flight_price': flight_price,
                'hotel_price': hotel_price}

    except:
        print('\n\n\n\n\n !!!!!!!!!!!!! ERROR. FAILED TO RETRIEVE DETAILS !!!!!!!!!!!!!')
    return result

# For each country get prices
for country in countries:
    chain = ActionChains(driver)

    # Click on div
    time.sleep(2)
    chain.move_to_element(country).click().perform()

    # Get all links from container divs
    try:
        wait = WebDriverWait(driver, timeout=10)
        wait.until(lambda d: d.find_element(By.CLASS_NAME, "city-list"))

    except Exception as exception:
        print(f'\n\n\n Failed to load elements \n\nError: {exception}')

    time.sleep(5)
    city_list = driver.execute_script('''
                return document.
                        getElementsByClassName('browse-list-category open')
                ''')
    
    # In case of multiple open boxes
    city_list = city_list[-1]

    # Get the links for each destination
    links = city_list.find_elements(By.CLASS_NAME, 'browse-data-entry')
    country_div = country.find_element(By.CLASS_NAME,
                                                'browse-data-route')

    # Get destination name
    country_name = country_div.find_element(By.XPATH, 'h3').text

    # Get destinations for country
    destinations = [collect_destination_details(index) for index in
                    range(len(links))]

    # Close chevron
    chevron_down = country.find_element(By.CLASS_NAME,
                                                'chevron-down')
    chain.move_to_element(chevron_down).click().perform()

    print(destinations)

driver.close()
driver.quit()
