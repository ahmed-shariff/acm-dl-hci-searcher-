===================
ACM DL Searcher
===================


.. image:: https://img.shields.io/pypi/v/acm_dl_hci_searcher.svg
        :target: https://pypi.python.org/pypi/acm_dl_hci_searcher

.. image:: https://readthedocs.org/projects/acm-dl-hci-searcher/badge/?version=latest
        :target: https://acm-dl-hci-searcher.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

A simple command line tool to collect the entries on a particular venue and in acm and run searches on them.


Install
-------

.. code:: sh
          
   pip install acm-dl-searcher

Usage
--------
If getting the entries from the `CHI 16`_ Conference:

* To get the entries of a particular venue:

  .. code:: sh

            acm-dl-searcher get 10.1145/2858036 --short-name "CHI 16""
  
  This will download all the entries and their abstracts. The short-name provided can be anything. The first parameter expected for ``amc-dl-searcher get`` is the doi of the venue.

* To list all the venues saved:

  .. code:: sh

            acm-dl-searcher list

* To search the from the saved venues:

  .. code:: sh

            acm-dl-searcher search "adaptive"

  This will search all the venues obtained through ``acm-dl-searcher get``, and list out the paper and titles that contain the phrase "adaptive" in the abstract or title. Currently the searcher uses a fuzzy search with a maximum difference of 2.

  To narrow the search to particular venue(s) use the option ``--venue-short-name-filter``:

  .. code:: sh

            acm-dl-searcher search "adaptive" --venue-short-name-filter "CHI"

  This will list out the matches from venues whose `short name` contain "CHI".

  To print out the abstracts as well use the option ``--print-abstracts``:
  
  .. code:: sh
            
     acm-dl-searcher search "adaptive" --print-abstracts

  To view the results on the browser use the option ``--html``:
  
  .. code:: sh
            
     acm-dl-searcher search "adaptive" --html

  


Credits
-------

This package was created with Cookiecutter_ and the `briggySmalls/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`briggySmalls/cookiecutter-pypackage`: https://github.com/briggySmalls/cookiecutter-pypackage
.. _`CHI 16`: https://dl.acm.org/doi/proceedings/10.1145/2858036
