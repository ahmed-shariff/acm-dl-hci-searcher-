"""Main module."""
import requests
import re
from bs4 import BeautifulSoup
import bibtexparser
from pathlib import Path
import json
from tqdm import tqdm

DATA_DIRECTORY = Path.home() / ".acm_dl_data"
SEARCH_STRING = "https://dl.acm.org/action/doSearch?LimitedContentGroupKey={key}&pageSize=50&startPage={page_id}"


# TODO: better logging
# TODO: parallelize data collection
def _process_venue_data_from_doi(doi, short_name=None, overwrite=False):
    """
    Takes a doi of a venue in acm and get the entries and abstract. The data will be cacheed in DATA_DIRECTORY. 
    Returns a dictionary containing the doi as keys and the details as values
    """    
    doi_file = _ensure_data_directory_exists() / (doi.replace("/", "_") + ".json")
    doi_title = bibtexparser.loads(requests.get(f"http://doi.org/{doi}", headers={"Accept": "application/x-bibtex"}).text).entries[0]["title"]
    print(f"Title: {doi_title}")
    _update_collection_info(doi_file.name, doi, doi_title, short_name)
    
    if not overwrite and doi_file.exists():
        with open(doi_file) as f:
            doi_list_details = json.load(f)
        return doi_list_details
    
    doi = doi.replace("/", "%2F")
    search_string = SEARCH_STRING.format(key=doi, page_id=0)
    response = requests.get(search_string)
    with open("temp.html", "w") as f:
        f.write(response.text)

    doi_matcher = re.compile(r">https:\/\/doi\.org\/\d{2}\.\d{4}\/\d+\.\d+<")
    # A working curl for doi meta data: curl --location --silent --header "Accept: application/x-bibtex" https://doi.org/10.1145/3313831.3376868
    doi_list = [i.rstrip("<").lstrip(">") for i in doi_matcher.findall(response.text)]
    total_hits = int(BeautifulSoup(response.text, features="html.parser").find("span", {"class": "hitsLength"}).get_text())
    print(f"Found {total_hits} hits")
    if total_hits > 50:
        page_id = 1
        while page_id * 50 < total_hits:
            print(f"Getting page {page_id}", end="\r")
            search_string = SEARCH_STRING.format(key=doi, page_id=page_id)
            response = requests.get(search_string)
            doi_list.extend([i.rstrip("<").lstrip(">") for i in doi_matcher.findall(response.text)])
            page_id += 1
        print()

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
    """Makes sure the data directory exists and returns the data directory path"""
    if not DATA_DIRECTORY.exists():
        DATA_DIRECTORY.mkdir()
    return DATA_DIRECTORY
    

def _get_collection_info():
    """
    Reads the global information file and return the contents as adictionary and the path to the file itself.
    """
    info_file = _ensure_data_directory_exists() / "info.json"
    if info_file.exists():
        with open(info_file) as f:
            info = json.load(f)
    else:
        info = {}
    return info, info_file
        

def _update_collection_info(file_name, doi, title, short_name):
    """
    Adds an entry to the gloabl infomation file. If the entry exists, will be overwritten.
    """
    info, info_file = _get_collection_info()

    info[file_name] = {"doi": doi, "title": title, "short_name": short_name}

    with open(info_file, "w") as f:
        json.dump(info, f)


def _get_entry_count(doi_file):
    """
    Given a file path, will return the number of entries in that file. If the file reading files, returns None.
    """
    try:
        with open(doi_file) as f:
            content = json.load(f)
        return len(content)
    except:
        return None


def _search(search_fn, venue_filter=None):
    """
    Takes a two functions as parameters. And returns a set of entries from the complete databases that return true for both functions.
    
    :search_fn: A callable that takes one parameter and returns true or false. 
                The paramter passed to this callable will be the content of an entry.
    :vanue_filter: A callable that takes three paramters: (short_name, title, doi) and return a boolean.
    :return: Returns a list of entries.
    """
    info, info_file = _get_collection_info()

    if venue_filter is None:
        venue_filter = lambda short_name, title, doi:True

    entries = []
    
    for doi_file, entry in info.items():
        if file_filter(entry["short_name"], entry["title"], entry["doi"]):
            with open(doi_file) as f:
                full_content_list = json.load(f)
            for content_dict in full_content_list:
                content = ":: ".join(content_dict.values())
                if search_fn(content):
                    entries.append(content_dict)

    return entries
                
