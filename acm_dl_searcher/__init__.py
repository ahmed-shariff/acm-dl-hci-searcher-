"""Top-level package for ACM DL HCI Searcher."""

from acm_dl_searcher.__main__ import _search
from acm_dl_searcher import search_operations

__author__ = """Ahmed Shariff"""
__email__ = 'shariff.mfa@outlook.com'
__version__ = '0.1.0-alpha.3'

search = _search

__all__ = [search, search_operations]
