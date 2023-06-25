import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import googlemaps
import plotly.graph_objects as go
from tabulate import tabulate

gmaps = googlemaps.Client(key='AIzaSyCsUzvhtiWMDzm4jBHbb1DhLBMBeDsf6B8')

URL = "https://booking-dp-fr.lastminute.com/s/hdp/search?origin=PAR&destination=A&datefrom=2023-06-20&dateto=2023-06-23&adults=2&search_mode=DP&sort=recommended&source=csw&businessProfileId=HOLIDAYSBOOKINGFR_PROMO2&bf_subsource=S07HPV10S07RR01&search_id=i4cr8nhwizlkd7sjit"
SCROLL_PAUSE_TIME = 1

# Create driver
driver = webdriver.Chrome()
driver.get(URL)
chain = ActionChains(driver)
time.sleep(5)
button = driver.find_element(By.XPATH, "//button[text()='Tout refuser']")
chain.move_to_element(button).click().perform()
time.sleep(5)

# Get scroll height
last_height = driver.execute_script("return document.body.scrollHeight")

count = 0
while count < 5:
    # Scroll down to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait to load page
    time.sleep(SCROLL_PAUSE_TIME)

    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    count += 1

time.sleep(2)

# Get all destinations
destinations = driver.find_elements(By.CLASS_NAME, 'openx-ui-card')

data = {"longitudes": [], "latitudes": [], "text": []}
results = []
# Find destination information
for destination in destinations:
    info = destination.find_element(By.CLASS_NAME, 'openx-ui-card-content')
    price_rating = destination.find_element(By.CLASS_NAME, 'openx-ui-card-details-right-mobile')

    # Get label from info
    label = info.find_element(By.CLASS_NAME, "openx-ui-card-label").text
    city = info.find_element(By.CLASS_NAME, "openx-ui-card-details-left-city").text
    country = info.find_element(By.CLASS_NAME, "openx-ui-card-details-left-country").text
    destination = info.find_element(By.CLASS_NAME, "openx-ui-card-details-left-description").text

    # Get price rating info
    direct_flight_or_layover = price_rating.find_element(By.CLASS_NAME, "openx-ui-card-details-left-flight").text
    rating = price_rating.find_element(By.CLASS_NAME, "openx-ui-card-details-left-rating")
    price = price_rating.find_element(By.CLASS_NAME, "openx-ui-card-price-container-value").text
    persons = price_rating.find_element(By.CLASS_NAME, "fZhwlq").text

    # Find coordinates
    location = gmaps.geocode(city + ", " + country)
    latitude = location.latitude
    longitude = location.longitude
    data["longitudes"].append(longitude)
    data["latitudes"].append(latitude)
    data["text"].append(city + ", " + country + " <br> " + "Price: " + price + " " + persons)
    result = [label, country, city, destination, direct_flight_or_layover, price, persons, latitude, longitude]
    results.append(result)

# # Plot data on a graph
layout = dict(title='Parsed flight data',
              geo=dict(projection={'type': 'robinson'},
                       showlakes=True,
                       lakecolor='rgb(0,191,255)'))
fig = go.Figure(data=go.Scattergeo(
    lon=data["longitudes"],
    lat=data["latitudes"],
    text=data["text"],
    hoverinfo="text",
    marker={'color': 'RebeccaPurple', 'size': 10},
    mode='markers'), layout=layout)
fig.update_geos(visible=True, resolution=110,
    showcountries=True, countrycolor="DarkGray"
)
fig.show()
fig.write_html("prices.html")

html_table = tabulate(results, tablefmt='html')
with open("price_table.html", "w", encoding="utf-8") as html:
    html.write(html_table)

print('done')
