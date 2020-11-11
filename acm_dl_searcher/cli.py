"""Console script for acm_dl_hci_searcher."""
import sys

import click
from tabulate import tabulate
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
def get():
    """Get the information for an entry"""
    doi = "10.1145/3313831"
    # TODO: Setting True for testing
    _process_venue_data_from_doi(doi, "CHI 20", verify=True)


@cli.command()
@click.option("--full-path", type=bool, default=False, is_flag=True)
def list(full_path):
    """List all the details"""
    info, info_file = _get_collection_info()
    if full_path:
        print("The file location is: {} \n".format(info_file.parent))
        
    table = [[i["short_name"], i["title"], i["doi"], _get_entry_count(info_file.parent / name), info_file.parent / name if full_path else name] for name, i in info.items()]
    headers = ["Short Name", "Title", "DOI", "# of entries" ,"File"]
    print(tabulate(table, headers, tablefmt="fancy_grid"))


@cli.command()
@click.argument("pattern", type=str)
@click.option("--venue-short-name-filter", type=str, default=None)
def search(pattern, venue_short_name_filter):
    """Search the database for matches"""
    results = _search(GenericSearchFunction(pattern), GenericVenueFilter(venue_short_name_filter, None, None))
    print([result["title"] for result in results], sep="\n")


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
