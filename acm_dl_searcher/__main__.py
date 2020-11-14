"""Main module."""
import requests
import re
from bs4 import BeautifulSoup
import bibtexparser
from pathlib import Path
import json
from tqdm import tqdm
import multiprocessing as mp
from tqdm.contrib.concurrent import process_map


DATA_DIRECTORY = Path.home() / ".acm_dl_data"
SEARCH_STRING = "https://dl.acm.org/action/doSearch?LimitedContentGroupKey={key}&pageSize=50&startPage={page_id}"


# TODO: better logging
# TODO: parallelize data collection
def _process_venue_data_from_doi(doi, short_name, overwrite=False, verify=False, force=False):
    """
    Takes a doi of a venue in acm and get the entries and abstract. The data will be cacheed in DATA_DIRECTORY. 
    Returns a dictionary containing the doi as keys and the details as values
    """    
    doi_file = _ensure_data_directory_exists() / (doi.replace("/", "_") + ".json")
    doi_entry = requests.get(f"http://doi.org/{doi}", headers={"Accept": "application/x-bibtex"}).text
    doi_title = bibtexparser.loads(doi_entry).entries[0]["title"]
    print(f"Title: {doi_title}")
    
    _update_collection_info(doi_file.name, doi, doi_title, short_name, force)

    doi_list_details = []
    if doi_file.exists():
        if not overwrite:
            with open(doi_file) as f:
                try:
                    doi_list_details = json.load(f)
                except json.decoder.JSONDecodeError:
                    pass
            if not verify:
                return doi_list_details
            print("File exists. Verifying if all entries exist.")
    
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

    max_workers = 2 * mp.cpu_count() + 2
    
    if total_hits > 50:
        page_id = 1
        search_strings = []
        while page_id * 50 < total_hits:
            search_strings.append(SEARCH_STRING.format(key=doi, page_id=page_id))
            page_id += 1

        print(f"Getting the urls for the {total_hits} entries")
        for urls in process_map(_get_doi_urls(doi_matcher), search_strings, max_workers=max_workers):
            doi_list.extend(urls)
        print()
        
    received_doi = [details["doi"] for details in doi_list_details]

    # Asynchronusly collect entries
    manager = mp.Manager()
    q = manager.Queue()    
    pool = mp.Pool(max_workers)

    #put listener to work first
    watcher = pool.apply_async(_bib_entry_collector, (q, doi_file, doi_list_details))

    print("Getting the entries")
    try:
        jobs = []
        for doi_url in doi_list:
            if doi_url.lstrip("https://doi.org/") in received_doi:
                continue
            jobs.append(pool.apply_async(_bib_entry_worker, (doi_url, q)))

        # collect results from the workers through the pool result queue
        for job in tqdm(jobs):
            job.get()

    finally:
        #now we are done, kill the listener
        q.put('kill')
        pool.close()
        pool.join()

        with open(doi_file) as f:
            doi_list_details = json.load(f)
            return doi_list_details


class _get_doi_urls:
    def __init__(self, doi_matcher):
        self.doi_matcher = doi_matcher

    def __call__(self, search_string):
        response = requests.get(search_string)
        return [i.rstrip("<").lstrip(">") for i in self.doi_matcher.findall(response.text)]


def _bib_entry_worker(doi_url, q):
    '''Get the doi entry and abstract of from a doi_url'''
    # Try five times before giving up
    for _ in range(5):
        try:
            details = bibtexparser.loads(requests.get(doi_url, headers={"Accept": "application/x-bibtex"}).text).entries[0]
            abstract_html = requests.get("https://dl.acm.org/doi/" + details["doi"]).text
            soup = BeautifulSoup(abstract_html, features="html.parser")
            abstract = soup.findAll("div", {"class": "abstractInFull"})[0].find("p").get_text()
            details["abstract"] = abstract
            q.put(details)
            break
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(e)


def _bib_entry_collector(q, doi_file, doi_list_details):
    '''listens for messages on the q, writes to file. '''
    with open(doi_file, 'w') as f:
        idx = 0
        while True:
            details = q.get()
            if details == 'kill' or idx % 50 == 0:
                with open(doi_file, "w") as f:
                    json.dump(doi_list_details, f)
                if details == 'kill':
                    break
            doi_list_details.append(details)
            idx += 1


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
        

def _update_collection_info(file_name, doi, title, short_name, force):
    """
    Adds an entry to the gloabl infomation file. If the entry exists, will be overwritten.
    """
    info, info_file = _get_collection_info()

    if file_name in info:
        if not force and short_name != info[file_name]["short_name"]:
            raise ValueError("Error: short-name provided does not match the one in database. " \
                             "If making sure all entries exist, run without the --short-name option to use the name in databse.\n"\
                             "To force the new name, use the option --force: acm-dl-searcher get <doi> --short-name <new-short-name> --force")
    else:
        if short_name is None:
            raise ValueError("Error: New entry: need paramter value for `short-name`. Pass value with option --short-name.")

    if short_name is not None and len(short_name) > 10:
        raise ValueError("Error: value for `--short-name` is too long (max 10 charachters).")
        
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
    root_dir = _ensure_data_directory_exists()
    print(f"Searching in `{root_dir}`")
    for doi_file, entry in info.items():
        if venue_filter(entry["short_name"], entry["title"], entry["doi"]):
            with open(root_dir / doi_file) as f:
                try:
                    full_content_list = json.load(f)
                except json.decoder.JSONDecodeError:
                    print(f"Warning: {entry['doi']} is empty.")
                    continue
            for content_dict in full_content_list:
                content = ":: ".join(content_dict.values())
                if search_fn(content):
                    entries.append(content_dict)

    return entries
                
