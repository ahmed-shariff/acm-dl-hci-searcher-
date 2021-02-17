"""Console script for acm_dl_hci_searcher."""
import sys

import click
from tabulate import tabulate
import textwrap
from acm_dl_searcher.__main__ import (_process_venue_data_from_doi,
                                      _get_collection_info,
                                      _get_entry_count,
                                      _search)
from acm_dl_searcher.search_operations import (GenericSearchFunction, GenericVenueFilter, RegexFilter)
from acm_dl_searcher._utils import _display_results_html


@click.group()
def cli():
    """Console script for acm_dl_hci_searcher."""
    pass

@cli.command()
@click.argument("doi")
@click.option("--short-name", type=str, help="The short name to use for this venue", default=None)
@click.option("--force", type=bool, help="Force the short name if different short name is being provided.", default=False, is_flag=True)
def get(doi, short_name=None, force=False):
    """Get the information for a value. Expects a doi of a venue."""
    try:
        _process_venue_data_from_doi(doi, short_name, verify=True, force=force)
    except ValueError as e:
        print(e)


@cli.command()
@click.option("--full-path", type=bool, default=False, is_flag=True)
def list(full_path):
    """List all the details"""
    info, info_file = _get_collection_info()
    if full_path:
        print("The file location is: {} \n".format(info_file.parent))
        
    table = [[textwrap.fill(i["short_name"], 10), textwrap.fill(i["title"], 60), i["doi"], _get_entry_count(info_file.parent / name), info_file.parent / name if full_path else name] for name, i in info.items()]
    headers = ["Short Name", "Title", "DOI", "# of entries" ,"File"]
    print(tabulate(table, headers, tablefmt="fancy_grid"))


@cli.command()
@click.argument("pattern", type=str)
@click.option("--venue-short-name-filter", type=str, default=None)
@click.option("--print-abstract", type=bool, is_flag=True, default=False)
@click.option("--html", type=bool, is_flag=True, default=False, help="Show results on browser")
@click.option("--re", type=bool, is_flag=True, default=False, help="Use regex matcher for pattern matching")
@click.option("--fuzzy-max-l-pattern", type=int, default=0, help="The maximum number of differences allowed from the pattern to add to the result")
@click.option("--fuzzy-max-l-venue", type=int, default=0, help="The maximum number of differences allowed from the venue-short-name-filter to add to the result")
def search(pattern, venue_short_name_filter, print_abstract, html, re, fuzzy_max_l_pattern, fuzzy_max_l_venue):
    """Search the database for matches"""
    if re:
        search_fn = RegexFilter(pattern)
        if fuzzy_max_l_pattern > 0:
            print("Ignoring `fuzzy-max-l-pattern`")
    else:
        search_fn = GenericSearchFunction(pattern, fuzzy_max_l_pattern)
    results = _search(search_fn, GenericVenueFilter(venue_short_name_filter, None, None, fuzzy_max_l_venue))
    
    formatted_results = [[result["doi"], result["year"], textwrap.fill(result["title"], 70), result["url"]] for result in results]
    if print_abstract:
        abstracts = [result["abstract"] for result in results]
        _formatted_results = []
        for i in range(len(formatted_results)):
            _formatted_results.append(formatted_results[i])
            _formatted_results.append(["", "", textwrap.fill(abstracts[i], 70), ""])
        formatted_results = _formatted_results
        header = ["DOI", "Year", "Title/Abstract", "URL"]
    else:
        header = ["DOI", "Year", "Title", "URL"]
    print(tabulate(formatted_results, header,tablefmt="fancy_grid"))
    if html:
        _display_results_html(pattern, results)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
