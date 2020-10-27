#!/usr/bin/env python
"""Tests for `acm_dl_hci_searcher` package."""
# pylint: disable=redefined-outer-name

import unittest
from click.testing import CliRunner

from acm_dl_hci_searcher import cli


class TestAcm_dl_hci_searcher(unittest.TestCase):
    """Tests for `acm_dl_hci_searcher` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'acm_dl_hci_searcher.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output
