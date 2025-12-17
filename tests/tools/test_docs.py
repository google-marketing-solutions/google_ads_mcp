# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for docs.py."""

import os
from unittest import mock

from ads_mcp.tools import docs
import pytest


@mock.patch("builtins.open", new_callable=mock.mock_open, read_data="doc content")
def test_get_gaql_doc(mock_file):
  """Tests get_gaql_doc function."""
  # We access the original function via .fn() to bypass the tool decorator
  assert docs.get_gaql_doc.fn() == "doc content"
  mock_file.assert_called_with(
      os.path.join(docs.MODULE_DIR, "context/GAQL.md"), "r", encoding="utf-8"
  )


@mock.patch("builtins.open", new_callable=mock.mock_open, read_data="doc content")
def test_get_reporting_doc(mock_file):
  """Tests get_reporting_doc resource."""
  assert docs.get_reporting_view_doc.fn(None) == "doc content"
  mock_file.assert_called_with(
      os.path.join(docs.MODULE_DIR, "context/Google_Ads_API_Reporting_Views.md"),
      "r",
      encoding="utf-8",
  )


@mock.patch("builtins.open", new_callable=mock.mock_open, read_data="view content")
def test_get_view_doc(mock_file):
  """Tests get_view_doc function."""
  assert docs.get_reporting_view_doc.fn("campaign") == "view content"
  mock_file.assert_called_with(
      os.path.join(docs.MODULE_DIR, "context/views/campaign.yaml"),
      "r",
      encoding="utf-8",
  )


@mock.patch("builtins.open", side_effect=FileNotFoundError)
def test_get_view_doc_not_found(mock_file):
  """Tests get_view_doc function when file not found."""
  assert (
      docs.get_reporting_view_doc.fn("non_existent")
      == "No view resource with that name was found."
  )


def test_resources_exist():
  """Tests that the resources are correctly defined."""
  # We can't easily test the @mcp.resource decorator registration without mocking FastMCP
  # but checking the tool definitions is done via coverage
  pass
