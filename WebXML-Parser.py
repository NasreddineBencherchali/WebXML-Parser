import re
import os
import xmltodict

try:
    import configparser as ConfigParser
except:
    import ConfigParser

print (r"""
 __    __     _              __  __          __  
/ / /\ \ \___| |__           \ \/ / /\/\    / /  
\ \/  \/ / _ \ '_ \   _____   \  / /    \  / /   
 \  /\  /  __/ |_) | |_____|  /  \/ /\/\ \/ /___ 
  \/  \/ \___|_.__/          /_/\_\/    \/\____/ 
                                                 
   ___                                           
  / _ \__ _ _ __ ___  ___ _ __                   
 / /_)/ _` | '__/ __|/ _ \ '__|                  
/ ___/ (_| | |  \__ \  __/ |                     
\/    \__,_|_|  |___/\___|_|                     
                                                 
""")


config = ConfigParser.ConfigParser()
config.readfp(open(r'Config.txt'))

web_xml_path = config.get("WebXML-Parser-Config","web_xml_path")
application_pages_path = config.get("WebXML-Parser-Config","application_pages_path")
application_name = config.get("WebXML-Parser-Config","application_name")
application_ip_address = config.get("WebXML-Parser-Config","application_ip_address")
https_bool = config.getboolean("WebXML-Parser-Config","https_bool")

# Building the list of all the available pages
list_of_all_pages = []
for root, dirs, files in os.walk(application_pages_path):
    for page_names in files:
        # Removes the '\' and replace them with '/' (To prepare the URL format) 
        full_path_of_page = os.path.join(root, page_names).replace('\\','/')
        
        # Checks weather the page is a .xhtml / .jsp
        if (".xhtml" in full_path_of_page) or (".jsp" in full_path_of_page):
            
            # We take only the string from the length of application_pages_path 
            full_path_of_page = full_path_of_page[len(application_pages_path) - 1:]
            
            list_of_all_pages.append(full_path_of_page)

# Get all the pages in the web.xml file
pages_in_web_xml = []
# This skip value is used to skip the comments in the XML file
skip = False
with open(web_xml_path, 'r') as web_xml:
    for lines in web_xml.readlines():
        if "<!--" in lines: 
            skip = True
        elif "-->" in lines:
            skip = False

        if not skip:
            if (".xhtml" in lines) or (".jsp" in lines) or ('*' in lines):
                lines = lines[lines.find('>') + 1 : ]
                lines = lines[ : lines.find('<')]
                pages_in_web_xml.append(lines)
        else:
            if "-->" in lines:
                # This condition ensures that if the comments ends in a single line.
                # We make the "skip" value return to it's default value.
                skip = False

# We remove the star from the pages that have a '*' in their path
# For example : /path/to/page/* => /path/to/page/
pages_in_web_xml_without_star = []
for star_pages in pages_in_web_xml:
    if "*" in star_pages:
        star_pages = star_pages[ : star_pages.find("*")]
        # We check if the pages is not empty
        if not star_pages == "":
            pages_in_web_xml_without_star.append(star_pages)



# Building the list of the pages that are not found in the WEB XML file
# Star pages are the pages that ends with a star such as (/pages/level1/level2/*)
list_of_pages_not_in_web_xml = []
# We loop through every page that existe in the folder
for every_page in list_of_all_pages:
    # We then check if it's not found inside the list of pages available in the Web.XML
    if every_page not in pages_in_web_xml:
        # This boolean is used to check weather the page contains an element of star pages
        # Example : every_page = /path/to/page/page.xhtml ; without_star_pages = /path/to/page/
        without_star_pages_bool = True
        for without_star_pages in pages_in_web_xml_without_star:
            if without_star_pages in every_page:
                without_star_pages_bool = False
                break
        
        if without_star_pages_bool:
            list_of_pages_not_in_web_xml.append(every_page)
                


########################
# CREATING THE LIST OF URL'S THAT ARE NOT PROTECTED BY AUTH-CONSTRAINT IN WEB XML (START) #
########################

# We parse the WEB.XML file for the <security-role> and the <security-constraint> tags
# To check if any URL's in the WEB XML file are missing the <auth-constraint> tag which mean that they can be accessed without authentication

# Using xmltodict library 
with open(web_xml_path) as fd:
    myWebXML = xmltodict.parse(fd.read())

# This list will contain the list of all the security roles in the application, that are listed in the WEB.XML file
list_of_security_role = []

# getting every role in the WEB XML
for role in myWebXML['web-app']['security-role']:
    list_of_security_role.append(role['role-name'])

# This list will contain all the Urls that do not have the <auth-constraint> or are misconfigured
list_of_non_protected_urls_in_web_xml = []

for j in myWebXML['web-app']['security-constraint']:
    auth_presence = False
    webresourcecollection = []

    for ele in j.items():
        if "web-resource-collection" in ele:
            webresourcecollection = ele
            
        if "auth-constraint" in ele:
            # Auth constraint bool
            auth_presence = True
            
            if type(ele[1]) == type(None):
                # Second case : if auth-constraint is found, we check if it's empty. 
                # If it is, we add the page found in url-pattern
                urlpattern = webresourcecollection[1]["url-pattern"]
                if type(urlpattern) == str:
                    list_of_non_protected_urls_in_web_xml.append(urlpattern)
                elif type(urlpattern) == list:
                    for urls in urlpattern:
                        list_of_non_protected_urls_in_web_xml.append(urls)
            else:
                # Third case : if auth-constraint is found and it's not empty, we check the roles 
                if type(ele[1]["role-name"]) == str:
                    if not (ele[1]["role-name"] in list_of_security_role):
                        urlpattern = webresourcecollection[1]["url-pattern"]
                        if type(urlpattern) == str:
                            list_of_non_protected_urls_in_web_xml.append(urlpattern)
                        elif type(urlpattern) == list:
                            for urls in urlpattern:
                                list_of_non_protected_urls_in_web_xml.append(urls)

                elif type(ele[1]["role-name"]) == list:
                    role_existance_bool = True
                    for each_role in ele[1]["role-name"]:
                        if not (each_role in list_of_security_role):
                            role_existance_bool = False
                    
                    if not role_existance_bool:
                        urlpattern = webresourcecollection[1]["url-pattern"]
                        if type(urlpattern) == str:
                            list_of_non_protected_urls_in_web_xml.append(urlpattern) 
                        elif type(urlpattern) == list:
                            for urls in urlpattern:
                                list_of_non_protected_urls_in_web_xml.append(urls)

    # First case : we check if auth-constraint is missing, if it is we add the page
    if not auth_presence:
        urlpattern = webresourcecollection[1]["url-pattern"]
        if type(urlpattern) == str:
            list_of_non_protected_urls_in_web_xml.append(urlpattern)  
        elif type(urlpattern) == list:
            for urls in urlpattern:
                list_of_non_protected_urls_in_web_xml.append(urls)

########################
# CREATING THE LIST OF URL'S THAT ARE NOT PROTECTED BY AUTH-CONSTRAINT IN WEB XML (END) #
########################


########################
# CREATING THE FILE THAT CONTAINS THE URLS (START) #
########################

# Building the list of URLS
list_of_urls = []

open("List_Of_URL.txt", 'w').close()

with open("List_Of_URL.txt", "w") as list_of_url_file:
    list_of_url_file.write("-- THESE ARE THE PAGES THAT ARE NOT LISTED IN THE WEB.XML FILE -- \n\n")
    for page in list_of_pages_not_in_web_xml:
        if https_bool:
            url = "https://"
        else:
            url = "http://"

        # Create the URL
        url = url + application_ip_address + "/" + application_name + "/" + page[1:]

        # Add the URL's to the file
        list_of_url_file.write(url + "\n")

        # Add the URL's to the list
        list_of_urls.append(url)
    
    list_of_url_file.write("\n-- THESE ARE THE PAGES THAT ARE NOT PROTECTED BY Auth-Constraint IN THE WEB.XML FILE -- \n\n")
    for page in list_of_non_protected_urls_in_web_xml:
        if https_bool:
            url = "https://"
        else:
            url = "http://"

        # Create the URL
        url = url + application_ip_address + "/" + application_name  + page

        # Add the URL's to the file
        list_of_url_file.write(url + "\n")

        # Add the URL's to the list
        if url not in list_of_urls:
            list_of_urls.append(url)

    print (r"[*]  List of URL's has been generated  [*]")

########################
# CREATING THE FILE THAT CONTAINS THE URLS (END) #
########################
