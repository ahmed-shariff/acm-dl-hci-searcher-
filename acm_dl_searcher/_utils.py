import webbrowser
from liquid import Liquid
from pathlib import Path

DATA_DIRECTORY = Path.home() / ".acm_dl_data"
SEARCH_STRING = "https://dl.acm.org/action/doSearch?LimitedContentGroupKey={key}&pageSize=50&startPage={page_id}"


def _ensure_data_directory_exists(sub_dir=None):
    """Makes sure the data directory exists and returns the data directory path"""
    if sub_dir:
        path = DATA_DIRECTORY / sub_dir
    else:
        path = DATA_DIRECTORY

    if not path.exists():
        path.mkdir(parents=True)
    return path


def _display_results_html(pattern, search_results):
    with open(Path(__file__).parent / "templates/search_result.html") as f:
        ret = Liquid(f).render(tempName = f"Results for : {pattern} (found {len(search_results)})", items = search_results)

    out_file = _ensure_data_directory_exists("temp") / "search_results.html"
    with open(out_file, "w") as f:
        f.write(ret)

    webbrowser.open("file://" + str(out_file.absolute()))
        
