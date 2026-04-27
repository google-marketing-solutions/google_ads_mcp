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

"""Tests for ad mutation tools."""

from unittest import mock
from ads_mcp.tools.mutations import ad
from fastmcp.exceptions import ToolError
from google.ads.googleads.errors import GoogleAdsException
import pytest


class MockGoogleAdsException(GoogleAdsException):
  """Mock GoogleAdsException for testing."""

  def __init__(self, errors):  # pylint: disable=super-init-not-called
    self.failure = mock.Mock()
    self.failure.errors = errors


@mock.patch("ads_mcp.tools.mutations.ad._get_client")
def test_create_responsive_search_ad_success(mock_get_client):
  """Tests create_responsive_search_ad successfully creates an ad."""
  mock_client = mock.Mock()
  mock_get_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service

  mock_response = mock.Mock()
  mock_response.results = [
      mock.Mock(resource_name="customers/123/adGroupAds/def")
  ]
  mock_service.mutate_ad_group_ads.return_value = mock_response

  result = ad.create_responsive_search_ad(
      customer_id="123",
      ad_group_resource_name="customers/123/adGroups/abc",
      headlines=["Headline 1", "Headline 2"],
      descriptions=["Description 1", "Description 2"],
      final_url="https://example.com",
  )

  assert result == {"resource_name": "customers/123/adGroupAds/def"}
  mock_service.mutate_ad_group_ads.assert_called_once()


@mock.patch("ads_mcp.tools.mutations.ad._get_client")
def test_create_responsive_search_ad_failure(mock_get_client):
  """Tests create_responsive_search_ad handles GoogleAdsException."""
  mock_client = mock.Mock()
  mock_get_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service

  mock_error = mock.Mock()
  mock_error.__str__ = mock.Mock(return_value="Invalid ad content")

  mock_service.mutate_ad_group_ads.side_effect = MockGoogleAdsException(
      [mock_error]
  )

  with pytest.raises(ToolError) as exc_info:
    ad.create_responsive_search_ad(
        customer_id="123",
        ad_group_resource_name="customers/123/adGroups/abc",
        headlines=["Headline 1", "Headline 2"],
        descriptions=["Description 1", "Description 2"],
        final_url="https://example.com",
    )

  assert "Invalid ad content" in str(exc_info.value)
