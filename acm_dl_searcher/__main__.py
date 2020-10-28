"""Main module."""
import requests
import re
from bs4 import BeautifulSoup
import bibtexparser
from pathlib import Path
import json
from tqdm import tqdm

DATA_DIRECTORY = Path.home() / ".acm_dl_data"
SEARCH_STRING = "https://dl.acm.org/action/doSearch?LimitedContentGroupKey={key}&pageSize=20&startPage=0"


def process_venue_data_from_doi(doi, overwrite=False):
    """
    Takes a doi of a venue in acm and get the entries and abstract. The data will be cacheed in DATA_DIRECTORY. 
    Returns a dictionary containing the doi as keys and the details as values
    """    
    doi_file = _ensure_data_directory_exists() / (doi.replace("/", "_") + ".json")
    if not overwrite and doi_file.exists():
        with open(doi_file) as f:
            doi_list_details = json.load(f)
        return doi_list_details

    doi = doi.replace("/", "%2F")
    search_string = SEARCH_STRING.format(key=doi)
    response = requests.get(search_string)
    with open("temp.html", "w") as f:
        f.write(response.text)

    doi_matcher = re.compile(r">https:\/\/doi\.org\/\d{2}\.\d{4}\/\d+\.\d+<")
    # A working curl for doi meta data: curl --location --silent --header "Accept: application/x-bibtex" https://doi.org/10.1145/3313831.3376868
    doi_list = [i.rstrip("<").lstrip(">") for i in doi_matcher.findall(response.text)]

    doi_list_details = []
    for doi_url in tqdm(doi_list):
        details = bibtexparser.loads(requests.get(doi_url, headers={"Accept": "application/x-bibtex"}).text).entries[0]
        abstract_html = requests.get("https://dl.acm.org/doi/" + details["doi"]).text
        soup = BeautifulSoup(abstract_html, features="html.parser")
        abstract = soup.findAll("div", {"class": "abstractInFull"})[0].find("p").get_text()
        details["abstract"] = abstract
        doi_list_details.append(details)

    with open(doi_file, "w") as f:
        json.dump(doi_list_details, f)

    return doi_list_details


def _ensure_data_directory_exists():
    if not DATA_DIRECTORY.exists():
        DATA_DIRECTORY.mkdir()
    return DATA_DIRECTORY
    
