# -*- coding: utf-8 -*-
import requests
from selenium import webdriver
from bs4 import BeautifulSoup, Comment
import urllib3

try:
    import configparser as ConfigParser
except:
    import ConfigParser

# This is added to supress the warnings of the insecure requests (SSL - verify=False)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print (r"""
   _         _                                
  /_\  _   _| |_ ___                          
 //_\\| | | | __/ _ \                         
/  _  \ |_| | || (_) |                        
\_/ \_/\__,_|\__\___/                         
                                              
   __                            _            
  /__\ ___  __ _ _   _  ___  ___| |_ ___ _ __ 
 / \/// _ \/ _` | | | |/ _ \/ __| __/ _ \ '__|
/ _  \  __/ (_| | |_| |  __/\__ \ ||  __/ |   
\/ \_/\___|\__, |\__,_|\___||___/\__\___|_|   
              |_|                             
""")

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

print (r"[*]  Creating the list of URL's...  [*]")

with open("List_Of_URL.txt", "r") as url_list:
    for url in url_list.readlines():
        if ("http" in url) and ("*" not in url):
            list_of_urls.append(url.strip())

# List of strings that are not accepted in the title (We ignore the URL)
# Where 'x' is the same element from the list, but without the leading white space.
list_of_unaccepted_strings_in_title = [x.strip() for x in config.get("WebXML-Parser-Config","list_of_unaccepted_strings_in_title").split(',')]
list_of_unaccepted_strings_in_content = [x.strip() for x in config.get("WebXML-Parser-Config","list_of_unaccepted_strings_in_content").split(',')]

# We filter the pages that are working from the pages that returns a 404 or something else
filtered_list_of_urls = []
for every_url in list_of_urls:
    if not proxy_bool:
        source_code = requests.get(every_url, verify=False).text
    else:
        source_code = requests.get(every_url, proxies=proxyDict, verify=False).text
        
    beautiful_source_code = BeautifulSoup(source_code, 'html.parser')
    
    # Bool to determine if we add or skip the URL
    unaccepted_string_bool = False

    # Bool to determine if the title of the page is none (from our beautifulsoup parser)
    none_title_bool = False

    # We loop through the list of unaccepted titles, if we got at least a match we break.
    # and we skip this URL
    for unaccepted_titles in list_of_unaccepted_strings_in_title:
        if type(beautiful_source_code.title) != type(None):
            if unaccepted_titles in beautiful_source_code.title.string:
                unaccepted_string_bool = True
                break
        else:
            # If the title is None we break and we check the content
            none_title_bool = True
            break

    # We jump here, if the title is equal to None
    if none_title_bool:
        for unaccepted_content in list_of_unaccepted_strings_in_content:
            if unaccepted_content in source_code:
                unaccepted_string_bool = True
                break
    # We jump here to make a double check in case if the title is not equal to None 
    # and the value of unaccepted_string_bool is still false
    elif not none_title_bool and not unaccepted_string_bool:
        for unaccepted_content in list_of_unaccepted_strings_in_content:
            if unaccepted_content in source_code:
                unaccepted_string_bool = True
                break

    if not unaccepted_string_bool :
        filtered_list_of_urls.append(every_url)

# Create an auto Requester of the pages with seleinum 
# Instantiate a selenium driver

print (r"[*]  Creating the file Filtered_List_Of_URL.txt ...  [*]")

open("Filtered_List_Of_URL.txt", 'w').close()

with open("Filtered_List_Of_URL.txt", "w") as Filtered_List_Of_URL:
    ("-- THESE ARE THE PAGES THAT ARE ACCESSIBLE AND SHOW SOMETHING ON THE SCREEN -- \n\n")
    for every_url in filtered_list_of_urls:
        Filtered_List_Of_URL.write(every_url + "\n")

screenshot_bool = str(input("Capture screenshots of the pages with Selenium (Y/N) : "))

if screenshot_bool.upper() == "Y":
    if proxy_bool:
        if https_bool:
            driver = start_driver(proxyDict["https"])
        else:
            driver = start_driver(proxyDict["http"])
    else:
        driver = start_driver()

    print (r"[*]  Requesting the URL's...  [*]")

    for every_url in filtered_list_of_urls:
        driver.get(every_url)
        get_screenshot(driver, every_url[every_url.rfind('/') + 1 :], ".png")

    driver.quit()
else:
    exit()
    