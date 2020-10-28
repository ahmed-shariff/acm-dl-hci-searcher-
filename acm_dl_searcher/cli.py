"""Console script for acm_dl_hci_searcher."""
import sys

import click
from acm_dl_searcher.__main__ import (_process_venue_data_from_doi,
                                      _get_collection_info)

@click.group()
def cli():
    """Console script for acm_dl_hci_searcher."""
    pass

@cli.command()
def get():
    """Get the information for an entry"""
    doi = "10.1145/3313831"
    # TODO: Setting True for testing
    _process_venue_data_from_doi(doi, "CHI 20")


@cli.command()
def list():
    """List all the details"""
    print(*(_get_collection_info()), sep="\n")

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
