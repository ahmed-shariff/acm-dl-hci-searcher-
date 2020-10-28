"""Console script for acm_dl_hci_searcher."""
import sys

import click
from acm_dl_searcher.__main__ import process_venue_data_from_doi

@click.command()
def main():
    """Console script for acm_dl_hci_searcher."""
    doi = "10.1145/3313831"
    # TODO: Setting True for testing
    print(process_venue_data_from_doi(doi, True))
    


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
