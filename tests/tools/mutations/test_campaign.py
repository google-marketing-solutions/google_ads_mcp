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

"""Tests for campaign mutation tools."""

from unittest import mock
from ads_mcp.tools.mutations import campaign
from fastmcp.exceptions import ToolError
from google.ads.googleads.errors import GoogleAdsException
import pytest


class MockGoogleAdsException(GoogleAdsException):
  """Mock GoogleAdsException for testing."""

  def __init__(self, errors):  # pylint: disable=super-init-not-called
    self.failure = mock.Mock()
    self.failure.errors = errors


@mock.patch("ads_mcp.tools.mutations.campaign._get_client")
def test_create_search_campaign_success(mock_get_client):
  """Tests create_search_campaign successfully creates a campaign."""
  mock_client = mock.Mock()
  mock_get_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service

  mock_response = mock.Mock()
  mock_response.results = [
      mock.Mock(resource_name="customers/123/campaigns/789")
  ]
  mock_service.mutate_campaigns.return_value = mock_response

  result = campaign.create_search_campaign(
      customer_id="123",
      name="Test Campaign",
      budget_resource_name="customers/123/campaignBudgets/456",
  )

  assert result == {"resource_name": "customers/123/campaigns/789"}
  mock_service.mutate_campaigns.assert_called_once()


@mock.patch("ads_mcp.tools.mutations.campaign._get_client")
def test_create_search_campaign_failure(mock_get_client):
  """Tests create_search_campaign handles GoogleAdsException."""
  mock_client = mock.Mock()
  mock_get_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service

  mock_error = mock.Mock()
  mock_error.__str__ = mock.Mock(return_value="Invalid campaign name")

  mock_service.mutate_campaigns.side_effect = MockGoogleAdsException(
      [mock_error]
  )

  with pytest.raises(ToolError) as exc_info:
    campaign.create_search_campaign(
        customer_id="123",
        name="Test Campaign",
        budget_resource_name="customers/123/campaignBudgets/456",
    )

  assert "Invalid campaign name" in str(exc_info.value)


@mock.patch("ads_mcp.tools.mutations.campaign._get_client")
def test_update_campaign_status_success(mock_get_client):
  """Tests update_campaign_status successfully updates status."""
  mock_client = mock.Mock()
  mock_get_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service

  mock_response = mock.Mock()
  mock_response.results = [
      mock.Mock(resource_name="customers/123/campaigns/789")
  ]
  mock_service.mutate_campaigns.return_value = mock_response

  result = campaign.update_campaign_status(
      customer_id="123",
      campaign_resource_name="customers/123/campaigns/789",
      status="ENABLED",
  )

  assert result == {"resource_name": "customers/123/campaigns/789"}
  mock_service.mutate_campaigns.assert_called_once()


@mock.patch("ads_mcp.tools.mutations.campaign._get_client")
def test_update_campaign_status_failure(mock_get_client):
  """Tests update_campaign_status handles GoogleAdsException."""
  mock_client = mock.Mock()
  mock_get_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service

  mock_error = mock.Mock()
  mock_error.__str__ = mock.Mock(return_value="Campaign not found")

  mock_service.mutate_campaigns.side_effect = MockGoogleAdsException(
      [mock_error]
  )

  with pytest.raises(ToolError) as exc_info:
    campaign.update_campaign_status(
        customer_id="123",
        campaign_resource_name="customers/123/campaigns/789",
        status="ENABLED",
    )

  assert "Campaign not found" in str(exc_info.value)


@mock.patch("ads_mcp.tools.mutations.campaign._get_client")
def test_update_campaign_geo_target_type_success(mock_get_client):
  """Tests update_campaign_geo_target_type successfully updates."""
  mock_client = mock.Mock()
  mock_get_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service

  mock_response = mock.Mock()
  mock_response.results = [
      mock.Mock(resource_name="customers/123/campaigns/789")
  ]
  mock_service.mutate_campaigns.return_value = mock_response

  result = campaign.update_campaign_geo_target_type(
      customer_id="123",
      campaign_resource_name="customers/123/campaigns/789",
      positive_geo_target_type="PRESENCE",
      negative_geo_target_type="PRESENCE",
  )

  assert result == {"resource_name": "customers/123/campaigns/789"}
  mock_service.mutate_campaigns.assert_called_once()


def test_update_campaign_geo_target_type_no_args():
  """Tests update_campaign_geo_target_type raises error without types."""
  with pytest.raises(ToolError) as exc_info:
    campaign.update_campaign_geo_target_type(
        customer_id="123",
        campaign_resource_name="customers/123/campaigns/789",
    )
  assert "At least one of" in str(exc_info.value)


@mock.patch("ads_mcp.tools.mutations.campaign._get_client")
def test_update_campaign_geo_target_type_failure(mock_get_client):
  """Tests update_campaign_geo_target_type handles GoogleAdsException."""
  mock_client = mock.Mock()
  mock_get_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service

  mock_error = mock.Mock()
  mock_error.__str__ = mock.Mock(return_value="Campaign not found")

  mock_service.mutate_campaigns.side_effect = MockGoogleAdsException(
      [mock_error]
  )

  with pytest.raises(ToolError) as exc_info:
    campaign.update_campaign_geo_target_type(
        customer_id="123",
        campaign_resource_name="customers/123/campaigns/789",
        positive_geo_target_type="PRESENCE",
    )

  assert "Campaign not found" in str(exc_info.value)
