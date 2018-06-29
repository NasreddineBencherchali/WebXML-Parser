import requests
from selenium import webdriver
from bs4 import BeautifulSoup, Comment

# Selenium INIT (START)
def start_driver(proxy=""):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1200x600')

    if proxy:
        options.add_argument('--proxy-server=' + proxy)

    driver = webdriver.Chrome(chrome_options=options)
    return driver

def get_screenshot(driver_instance, path_to_image, image_ext):
    return driver_instance.get_screenshot_as_file(path_to_image + image_ext)
# Selenium INIT (END)

########################
# CREATING THE AUTO REQUESTER FROM THE FILTERD URL LIST (START) #
########################

list_of_urls = []

with open("List_Of_URL.txt", "r") as url_list:
    for url in url_list.readlines():
        if "http" in url:
            print url
            list_of_urls.append(url.strip())

# We filter the pages that are working from the pages that returns a 404 or something else
filtered_list_of_urls = []
for every_url in list_of_urls:
    source_code = requests.get(every_url).text
    beautiful_source_code = BeautifulSoup(source_code, 'html.parser')
    if ("404" or "403" ) not in beautiful_source_code.title.string :
        filtered_list_of_urls.append(every_url)

# Create an auto Requester of the pages with seleinum 
# Instantiate a selenium driver
driver = start_driver()
for every_url in filtered_list_of_urls:
    driver.get(every_url)
    get_screenshot(driver, every_url[every_url.rfind('/') + 1 :], ".png")