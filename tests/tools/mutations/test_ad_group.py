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

"""Tests for ad group mutation tools."""

from unittest import mock
from ads_mcp.tools.mutations import ad_group
from fastmcp.exceptions import ToolError
from google.ads.googleads.errors import GoogleAdsException
import pytest


class MockGoogleAdsException(GoogleAdsException):
  """Mock GoogleAdsException for testing."""

  def __init__(self, errors):  # pylint: disable=super-init-not-called
    self.failure = mock.Mock()
    self.failure.errors = errors


@mock.patch("ads_mcp.tools.mutations.ad_group._get_client")
def test_create_ad_group_success(mock_get_client):
  """Tests create_ad_group successfully creates an ad group."""
  mock_client = mock.Mock()
  mock_get_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service

  mock_response = mock.Mock()
  mock_call = mock.Mock()
  mock_call.resource_name = "customers/123/adGroups/abc"
  mock_response.results = [mock_call]
  mock_service.mutate_ad_groups.return_value = mock_response

  result = ad_group.create_ad_group(
      customer_id="123",
      name="Test Ad Group",
      campaign_resource_name="customers/123/campaigns/789",
  )

  assert result == {"resource_name": "customers/123/adGroups/abc"}
  mock_service.mutate_ad_groups.assert_called_once()


@mock.patch("ads_mcp.tools.mutations.ad_group._get_client")
def test_create_ad_group_failure(mock_get_client):
  """Tests create_ad_group handles GoogleAdsException."""
  mock_client = mock.Mock()
  mock_get_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service

  mock_error = mock.Mock()
  mock_error.__str__ = mock.Mock(return_value="Invalid ad group name")

  mock_service.mutate_ad_groups.side_effect = MockGoogleAdsException(
      [mock_error]
  )

  with pytest.raises(ToolError) as exc_info:
    ad_group.create_ad_group(
        customer_id="123",
        name="Test Ad Group",
        campaign_resource_name="customers/123/campaigns/789",
    )

  assert "Invalid ad group name" in str(exc_info.value)


@mock.patch("ads_mcp.tools.mutations.ad_group._get_client")
def test_update_ad_group_status_success(mock_get_client):
  """Tests update_ad_group_status successfully updates status."""
  mock_client = mock.Mock()
  mock_get_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service

  mock_response = mock.Mock()
  mock_call = mock.Mock()
  mock_call.resource_name = "customers/123/adGroups/abc"
  mock_response.results = [mock_call]
  mock_service.mutate_ad_groups.return_value = mock_response

  result = ad_group.update_ad_group_status(
      customer_id="123",
      ad_group_resource_name="customers/123/adGroups/abc",
      status="PAUSED",
  )

  assert result == {"resource_name": "customers/123/adGroups/abc"}
  mock_service.mutate_ad_groups.assert_called_once()


@mock.patch("ads_mcp.tools.mutations.ad_group._get_client")
def test_update_ad_group_status_failure(mock_get_client):
  """Tests update_ad_group_status handles GoogleAdsException."""
  mock_client = mock.Mock()
  mock_get_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service

  mock_error = mock.Mock()
  mock_error.__str__ = mock.Mock(return_value="Ad group not found")

  mock_service.mutate_ad_groups.side_effect = MockGoogleAdsException(
      [mock_error]
  )

  with pytest.raises(ToolError) as exc_info:
    ad_group.update_ad_group_status(
        customer_id="123",
        ad_group_resource_name="customers/123/adGroups/abc",
        status="PAUSED",
    )

  assert "Ad group not found" in str(exc_info.value)
