# WebXML-Parser  [![python](https://img.shields.io/badge/Python-3-green.svg?style=style=flat-square)](https://www.python.org/downloads/)  [![version](https://img.shields.io/badge/Version-Beta-blue.svg?style=style=flat-square)](https://twitter.com/nas_bench)

**WebXML-Parser** Takes the web pages of a JEE project (xhtml, jsp), and returns a file with the URL's that are not defined in the **WEB.xml** (Can be accessed without authentication) (Glassfish)

It also checks for the pages (URL's) that are not protected by an **Auth-Constraint**

**AutoRequester** Will request each url in that generated file, and takes a screenshot of it

## Requirements

* **ChromeDriver** - [Download Link](https://goo.gl/gtYUc1) (Copy downloaded file in the root of the python installation)

Install requirements :

```bash
pip install -r Requirements.txt
```

## Usage

To get started, modify the Config.txt file with the correct paths and values and run :

```bash
python WebXML-Parser.py
```

To requeste the fetched pages automatically, use :

```bash
python AutoRequester.py
```
