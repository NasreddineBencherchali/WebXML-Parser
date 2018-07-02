import re
import os
import xml.etree.ElementTree as ET

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

        # We take only the string from the "pages" position 
        full_path_of_page = full_path_of_page[full_path_of_page.find('pages') - 1:]
        
        list_of_all_pages.append(full_path_of_page)

# Get the content of the WEB XML file
web_xml_content = ""
with open(web_xml_path, 'r') as web_xml:
    for lines in web_xml.readlines():
        web_xml_content += lines

# Building the list of the pages that are not found in the WEB XML file
list_of_pages_not_in_web_xml = []
for page in list_of_all_pages:
    if page not in web_xml_content:
        list_of_pages_not_in_web_xml.append(page)



########################
# CREATING THE LIST OF URL'S THAT ARE NOT PROTECTED BY AUTH-CONSTRAINT IN WEB XML (START) #
########################

# We parse the WEB.XML file for the <security-role> and the <security-constraint> tags
# To check if any URL's in the WEB XML file are missing the <auth-constraint> tag which mean that they can be accessed without authentication

tree = ET.parse(web_xml_path)
root = tree.getroot()

# This list will contain the list of all the security roles in the application, that are listed in the WEB.XML file
list_of_security_role = []

# Security Role (WEB.XML) Example 
"""
    <security-role>
            <description>  Description  </description> # Level [0]
            <role-name>  Role_Name  </role-name> # Level [1]
    </security-role>

"""
for each_element in root:
    if "security-role" in each_element.tag:
        # Sometimes the description tag is empty. Which results in a None variable
        if type(each_element[0].text) != type(None):
            role_description = each_element[0].text
            role_name = each_element[1].text

            # We add only the role name to the list (for later checks)
            list_of_security_role.append(role_name)

# This list will contain all the Urls that do not have the <auth-constraint> or are misconfigured
list_of_non_protected_urls_in_web_xml = []

# Security Constraint (WEB.XML) Example 
"""
    <security-constraint>
        <display-name>  Pentester_010_001_Constraint  </display-name> # Level [0]
        <web-resource-collection> # Level [1]
            <web-resource-name>  Pentester_010_001_Constraint  </web-resource-name> # Level [1][0]
            <description/> # Level [1][1]
            <url-pattern>  /pages/administration/suividemandeCD/listDemande1.xhtml  </url-pattern> # Level [1][2]
        </web-resource-collection> # Level [1][0]
        <auth-constraint> # Level [2]
            <description/> # Level [2][0]
            <role-name>  Pentester_010_001  </role-name> # Level [2][1]
        </auth-constraint> # Level [2]
    </security-constraint>

"""

for each_element in root:
    if "security-constraint" in each_element.tag:
        url_pattern = each_element[1][2].text
        web_resource_name = each_element[1][0].text

        if type(each_element[2]) != type(None):
            auth_constraint_role_name = each_element[2][1].text

            # We check if the role_name in the <auth-constraint> tag is available in the LIST OF ROLES AND in the <web-resource-collection> 
            if not ((auth_constraint_role_name in web_resource_name) and (auth_constraint_role_name in list_of_security_role)):
                list_of_non_protected_urls_in_web_xml.append((url_pattern, web_resource_name))
       
        else:
            list_of_non_protected_urls_in_web_xml.append((url_pattern, web_resource_name))

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
        url = url + application_ip_address + "/" + application_name + page

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
        url = url + application_ip_address + "/" + application_name + page[0]

        # Add the URL's to the file
        list_of_url_file.write(url + "\n")

        # Add the URL's to the list
        if url not in list_of_urls:
            list_of_urls.append(url)

    print (r"[*]  List of URL's has been generated  [*]")

########################
# CREATING THE FILE THAT CONTAINS THE URLS (END) #
########################
