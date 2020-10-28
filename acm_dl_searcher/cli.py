"""Console script for acm_dl_hci_searcher."""
import sys

import click
from acm_dl_searcher.__main__ import process_doi

@click.command()
def main():
    """Console script for acm_dl_hci_searcher."""
    process_doi()


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
