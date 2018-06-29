import requests
from selenium import webdriver
from bs4 import BeautifulSoup, Comment
import ConfigParser

config = ConfigParser.ConfigParser()
config.readfp(open(r'Config.txt'))

proxyDict = {}
proxy_bool = config.getboolean("WebXML-Parser-Config","proxy_bool")
https_bool = config.getboolean("WebXML-Parser-Config","https_bool")

if proxy_bool:
    http_proxy = config.get("WebXML-Parser-Config","http_proxy_value")
    https_proxy = config.get("WebXML-Parser-Config","https_proxy_value")
    ftp_proxy = config.get("WebXML-Parser-Config","ftp_proxy_value")

    proxyDict = { 
              "http"  : http_proxy, 
              "https" : https_proxy, 
              "ftp"   : ftp_proxy
            }

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
    if not proxy_bool:
        source_code = requests.get(every_url, verify=False).text
    else:
        source_code = requests.get(every_url, proxies=proxyDict, verify=False).text
        
    beautiful_source_code = BeautifulSoup(source_code, 'html.parser')
    if ("404" or "403" ) not in beautiful_source_code.title.string :
        filtered_list_of_urls.append(every_url)

# Create an auto Requester of the pages with seleinum 
# Instantiate a selenium driver

if proxy_bool:
    if https_bool:
        driver = start_driver(proxyDict["https"])
    else:
        driver = start_driver(proxyDict["http"])
else:
    driver = start_driver()

for every_url in filtered_list_of_urls:
    driver.get(every_url)
    get_screenshot(driver, every_url[every_url.rfind('/') + 1 :], ".png")

driver.quit()