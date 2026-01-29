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

"""Tests for the view generation script."""
from unittest import mock

from ads_mcp.scripts.generate_views import get_fields_obj
from ads_mcp.scripts.generate_views import get_view_json
from ads_mcp.scripts.generate_views import get_view_json_url
from ads_mcp.scripts.generate_views import save_view_yaml
from ads_mcp.scripts.generate_views import update_views_yaml
import pytest


def test_get_view_json_url():
  """Tests the get_view_json_url function."""
  assert (
      get_view_json_url("campaign")
      == "https://gaql-query-builder.uc.r.appspot.com/schemas/v23/campaign.json"
  )


@pytest.mark.asyncio
@mock.patch("httpx.AsyncClient.get", new_callable=mock.AsyncMock)
async def test_get_view_json(mock_get):
  """Tests the get_view_json function."""
  mock_response = mock.MagicMock()
  mock_response.json.return_value = {"name": "campaign"}
  mock_get.return_value = mock_response
  assert await get_view_json("campaign") == {"name": "campaign"}


def test_get_fields_obj():
  """Tests the get_fields_obj function."""
  view_json = {
      "attributes": ["campaign.id"],
      "segments": [],
      "metrics": [],
      "fields": {
          "campaign.id": {
              "field_details": {
                  "name": "campaign.id",
                  "description": "The ID of the campaign.",
                  "category": "ATTRIBUTE",
                  "data_type": "INT64",
                  "is_repeated": False,
                  "enum_values": [],
                  "filterable": True,
                  "sortable": True,
              }
          }
      },
  }
  expected = {
      "campaign.id": {
          "description": "The ID of the campaign.",
          "data_type": "INT64",
          "is_repeated": False,
          "filterable": True,
          "sortable": True,
      }
  }
  assert get_fields_obj(view_json, "attributes") == expected


@pytest.mark.asyncio
@mock.patch(
    "ads_mcp.scripts.generate_views.get_view_json", new_callable=mock.AsyncMock
)
@mock.patch("builtins.open", new_callable=mock.mock_open)
@mock.patch("yaml.safe_dump")
async def test_save_view_yaml(mock_safe_dump, mock_open, mock_get_view_json):
  """Tests the save_view_yaml function."""
  mock_get_view_json.return_value = {
      "display_name": "Campaign",
      "name": "campaign",
      "description": "A campaign.",
      "attributes": ["campaign.id"],
      "segments": [],
      "metrics": [],
      "fields": {
          "campaign.id": {
              "field_details": {
                  "name": "campaign.id",
                  "description": "The ID of the campaign.",
                  "category": "ATTRIBUTE",
                  "data_type": "INT64",
                  "is_repeated": False,
                  "enum_values": [],
                  "filterable": True,
                  "sortable": True,
              }
          }
      },
  }
  await save_view_yaml("campaign", path="/fake/dir")
  mock_open.assert_called_with(
      "/fake/dir/campaign.yaml", "w", encoding="utf-8"
  )
  mock_safe_dump.assert_called_once()


@pytest.mark.asyncio
@mock.patch("os.path.isfile")
@mock.patch("builtins.open", new_callable=mock.mock_open)
@mock.patch("yaml.safe_load")
@mock.patch(
    "ads_mcp.scripts.generate_views.save_view_yaml",
    new_callable=mock.AsyncMock,
)
async def test_update_views_yaml(
    mock_save_view_yaml, mock_safe_load, mock_open, mock_isfile
):
  """Tests the update_views_yaml function."""
  mock_isfile.return_value = True
  mock_open.return_value.read.return_value = "old_version"
  mock_safe_load.return_value = ["campaign", "ad_group"]
  await update_views_yaml()
  assert mock_save_view_yaml.call_count == 2
  mock_open.assert_any_call(
      mock.ANY, "w", encoding="utf-8"
  )  # Check for write call
