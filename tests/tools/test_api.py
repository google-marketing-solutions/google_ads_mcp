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

"""Tests for the API tools."""

from unittest import mock

from ads_mcp.tools import api
import proto
import pytest


@pytest.fixture(autouse=True)
def reset_ads_client():
  """Resets the cached GoogleAdsClient instance before each test."""
  api._ADS_CLIENT = None
  yield
  api._ADS_CLIENT = None


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        (
            "SELECT campaign.id FROM campaign",
            (
                "SELECT campaign.id FROM campaign PARAMETERS"
                " omit_unselected_resource_names=true"
            ),
        ),
        (
            "SELECT campaign.id FROM campaign PARAMETERS include_drafts=true",
            (
                "SELECT campaign.id FROM campaign PARAMETERS"
                " include_drafts=true omit_unselected_resource_names=true"
            ),
        ),
        (
            (
                "SELECT campaign.id FROM campaign PARAMETERS"
                " omit_unselected_resource_names=true"
            ),
            (
                "SELECT campaign.id FROM campaign PARAMETERS"
                " omit_unselected_resource_names=true"
            ),
        ),
    ],
)
def test_preprocess_gaql(query, expected):
  """Tests the preprocess_gaql function."""
  assert api.preprocess_gaql(query) == expected


def test_format_value(mocker):
  """Tests the format_value function."""
  # Test with a proto.Message
  mock_message = mock.Mock(spec=proto.Message)
  mocker.patch.object(proto.Message, "to_dict", return_value={"key": "value"})
  assert api.format_value(mock_message) == {"key": "value"}

  # Test with a proto.Enum
  mock_enum = mock.Mock(spec=proto.Enum)
  mock_enum.name = "ENUM_VALUE"
  assert api.format_value(mock_enum) == "ENUM_VALUE"

  # Test with a simple type
  assert api.format_value("string") == "string"
  assert api.format_value(123) == 123


@mock.patch("ads_mcp.tools.api.GoogleAdsClient")
def test_list_accessible_accounts(mock_google_ads_client):
  """Tests the list_accessible_accounts function."""
  mock_client_instance = mock_google_ads_client.load_from_storage.return_value
  mock_service = mock_client_instance.get_service.return_value
  mock_service.list_accessible_customers.return_value.resource_names = [
      "customers/123",
      "customers/456",
  ]
  assert api.list_accessible_accounts.fn() == ["123", "456"]


@mock.patch("ads_mcp.tools.api.GoogleAdsClient")
def test_execute_gaql(mock_google_ads_client):
  """Tests the execute_gaql function."""
  mock_client_instance = mock_google_ads_client.load_from_storage.return_value
  mock_ads_service = mock_client_instance.get_service.return_value
  mock_ads_service.search_stream.return_value = [
      mock.Mock(
          results=[mock.Mock()], field_mask=mock.Mock(paths=["campaign.id"])
      )
  ]
  with mock.patch("ads_mcp.tools.api.get_nested_attr", return_value="123"):
    assert api.execute_gaql.fn("SELECT campaign.id FROM campaign", "123") == [
        {"campaign.id": "123"}
    ]
