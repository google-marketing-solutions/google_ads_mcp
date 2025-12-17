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

"""Tests for stdio.py."""

from unittest import mock

from ads_mcp import stdio
import pytest


@mock.patch("ads_mcp.stdio.mcp_server")
@mock.patch("ads_mcp.stdio.api")
@mock.patch("ads_mcp.stdio.update_views_yaml")
def test_main(mock_update_views, mock_api, mock_mcp_server):
  """Tests main function."""
  with mock.patch("ads_mcp.stdio.asyncio.run"):
    stdio.main()

  mock_update_views.assert_called_once()
  mock_api.get_ads_client.assert_called_once()
  mock_mcp_server.run.assert_called_once_with(transport="stdio")
