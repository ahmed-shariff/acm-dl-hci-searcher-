"""Console script for acm_dl_hci_searcher."""
import sys

import click
from tabulate import tabulate
import textwrap
from acm_dl_searcher.__main__ import (_process_venue_data_from_doi,
                                      _get_collection_info,
                                      _get_entry_count,
                                      _search)
from acm_dl_searcher.search_operations import (GenericSearchFunction, GenericVenueFilter)

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
def search(pattern, venue_short_name_filter, print_abstract):
    """Search the database for matches"""
    results = _search(GenericSearchFunction(pattern), GenericVenueFilter(venue_short_name_filter, None, None))
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


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
