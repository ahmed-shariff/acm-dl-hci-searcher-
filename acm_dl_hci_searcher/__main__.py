"""Main module."""
import requests
import re

def process_doi():
    search_string = "https://dl.acm.org/action/doSearch?LimitedContentGroupKey={key}&pageSize=20&startPage=1"
    doi = "10.1145/3313831"
    doi = doi.replace("/", "%2F")
    search_string = search_string.format(key=doi)
    response = requests.get(search_string)
    re.compile(r"https://doi.org/10.1145/3313831.3376868")
    print(response.text)
    
    
