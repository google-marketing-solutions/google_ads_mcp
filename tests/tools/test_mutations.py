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

"""Tests for the mutations tools."""

from unittest import mock
from ads_mcp.tools import mutations
from fastmcp.exceptions import ToolError
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v24.enums.types.budget_delivery_method import (
    BudgetDeliveryMethodEnum,
)
import pytest

# pylint: disable=protected-access


class MockGoogleAdsException(GoogleAdsException):
  """Mock GoogleAdsException for testing."""

  def __init__(self, errors):  # pylint: disable=super-init-not-called
    self.failure = mock.Mock()
    self.failure.errors = errors


def test_resolve_enum_success():
  """Tests _resolve_enum with valid input."""
  enum_type = BudgetDeliveryMethodEnum.BudgetDeliveryMethod
  result = mutations._resolve_enum(enum_type, "STANDARD", "delivery_method")
  assert result == enum_type.STANDARD


def test_resolve_enum_case_insensitive():
  """Tests _resolve_enum with case-insensitive input."""
  enum_type = BudgetDeliveryMethodEnum.BudgetDeliveryMethod
  result = mutations._resolve_enum(enum_type, "standard", "delivery_method")
  assert result == enum_type.STANDARD


def test_resolve_enum_invalid():
  """Tests _resolve_enum with invalid input."""
  enum_type = BudgetDeliveryMethodEnum.BudgetDeliveryMethod
  with pytest.raises(ToolError) as exc_info:
    mutations._resolve_enum(enum_type, "INVALID_VALUE", "delivery_method")
  assert "Invalid delivery_method" in str(exc_info.value)
  assert "STANDARD" in str(exc_info.value)


@mock.patch("ads_mcp.tools.mutations.get_ads_client")
def test_create_campaign_budget_success(mock_get_ads_client):
  """Tests create_campaign_budget successfully creates a budget."""
  mock_client = mock.Mock()
  mock_get_ads_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service

  mock_response = mock.Mock()
  mock_response.results = [
      mock.Mock(resource_name="customers/123/campaignBudgets/456")
  ]
  mock_service.mutate_campaign_budgets.return_value = mock_response

  result = mutations.create_campaign_budget(
      customer_id="123",
      name="Test Budget",
      amount_micros=1000000,
  )

  assert result == {"resource_name": "customers/123/campaignBudgets/456"}
  mock_service.mutate_campaign_budgets.assert_called_once()


@mock.patch("ads_mcp.tools.mutations.get_ads_client")
def test_create_campaign_budget_failure(mock_get_ads_client):
  """Tests create_campaign_budget handles GoogleAdsException."""
  mock_client = mock.Mock()
  mock_get_ads_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service

  mock_error = mock.Mock()
  mock_error.__str__ = mock.Mock(return_value="Invalid budget name")

  mock_failure = mock.Mock()
  mock_failure.errors = [mock_error]

  mock_service.mutate_campaign_budgets.side_effect = MockGoogleAdsException(
      [mock_error]
  )

  with pytest.raises(ToolError) as exc_info:
    mutations.create_campaign_budget(
        customer_id="123",
        name="Test Budget",
        amount_micros=1000000,
    )

  assert "Invalid budget name" in str(exc_info.value)


@mock.patch("ads_mcp.tools.mutations.get_ads_client")
def test_create_search_campaign_success(mock_get_ads_client):
  """Tests create_search_campaign successfully creates a campaign."""
  mock_client = mock.Mock()
  mock_get_ads_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service

  mock_response = mock.Mock()
  mock_response.results = [
      mock.Mock(resource_name="customers/123/campaigns/789")
  ]
  mock_service.mutate_campaigns.return_value = mock_response

  result = mutations.create_search_campaign(
      customer_id="123",
      name="Test Campaign",
      budget_resource_name="customers/123/campaignBudgets/456",
  )

  assert result == {"resource_name": "customers/123/campaigns/789"}
  mock_service.mutate_campaigns.assert_called_once()


@mock.patch("ads_mcp.tools.mutations.get_ads_client")
def test_create_search_campaign_failure(mock_get_ads_client):
  """Tests create_search_campaign handles GoogleAdsException."""
  mock_client = mock.Mock()
  mock_get_ads_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service

  mock_error = mock.Mock()
  mock_error.__str__ = mock.Mock(return_value="Invalid campaign name")

  mock_service.mutate_campaigns.side_effect = MockGoogleAdsException(
      [mock_error]
  )

  with pytest.raises(ToolError) as exc_info:
    mutations.create_search_campaign(
        customer_id="123",
        name="Test Campaign",
        budget_resource_name="customers/123/campaignBudgets/456",
    )

  assert "Invalid campaign name" in str(exc_info.value)


@mock.patch("ads_mcp.tools.mutations.get_ads_client")
def test_create_ad_group_success(mock_get_ads_client):
  """Tests create_ad_group successfully creates an ad group."""
  mock_client = mock.Mock()
  mock_get_ads_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service

  mock_response = mock.Mock()
  mock_response.results = [
      mock.Mock(resource_name="customers/123/adGroups/abc")
  ]
  mock_service.mutate_ad_groups.return_value = mock_response

  result = mutations.create_ad_group(
      customer_id="123",
      name="Test Ad Group",
      campaign_resource_name="customers/123/campaigns/789",
  )

  assert result == {"resource_name": "customers/123/adGroups/abc"}
  mock_service.mutate_ad_groups.assert_called_once()


@mock.patch("ads_mcp.tools.mutations.get_ads_client")
def test_create_ad_group_failure(mock_get_ads_client):
  """Tests create_ad_group handles GoogleAdsException."""
  mock_client = mock.Mock()
  mock_get_ads_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service

  mock_error = mock.Mock()
  mock_error.__str__ = mock.Mock(return_value="Invalid ad group name")

  mock_service.mutate_ad_groups.side_effect = MockGoogleAdsException(
      [mock_error]
  )

  with pytest.raises(ToolError) as exc_info:
    mutations.create_ad_group(
        customer_id="123",
        name="Test Ad Group",
        campaign_resource_name="customers/123/campaigns/789",
    )

  assert "Invalid ad group name" in str(exc_info.value)


@mock.patch("ads_mcp.tools.mutations.get_ads_client")
def test_create_responsive_search_ad_success(mock_get_ads_client):
  """Tests create_responsive_search_ad successfully creates an ad."""
  mock_client = mock.Mock()
  mock_get_ads_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service

  mock_response = mock.Mock()
  mock_response.results = [
      mock.Mock(resource_name="customers/123/adGroupAds/def")
  ]
  mock_service.mutate_ad_group_ads.return_value = mock_response

  result = mutations.create_responsive_search_ad(
      customer_id="123",
      ad_group_resource_name="customers/123/adGroups/abc",
      headlines=["Headline 1", "Headline 2"],
      descriptions=["Description 1", "Description 2"],
      final_url="https://example.com",
  )

  assert result == {"resource_name": "customers/123/adGroupAds/def"}
  mock_service.mutate_ad_group_ads.assert_called_once()


@mock.patch("ads_mcp.tools.mutations.get_ads_client")
def test_create_responsive_search_ad_failure(mock_get_ads_client):
  """Tests create_responsive_search_ad handles GoogleAdsException."""
  mock_client = mock.Mock()
  mock_get_ads_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service

  mock_error = mock.Mock()
  mock_error.__str__ = mock.Mock(return_value="Invalid ad content")

  mock_service.mutate_ad_group_ads.side_effect = MockGoogleAdsException(
      [mock_error]
  )

  with pytest.raises(ToolError) as exc_info:
    mutations.create_responsive_search_ad(
        customer_id="123",
        ad_group_resource_name="customers/123/adGroups/abc",
        headlines=["Headline 1", "Headline 2"],
        descriptions=["Description 1", "Description 2"],
        final_url="https://example.com",
    )

  assert "Invalid ad content" in str(exc_info.value)


@mock.patch("ads_mcp.tools.mutations.get_ads_client")
def test_create_keywords_success(mock_get_ads_client):
  """Tests create_keywords successfully creates keywords."""
  mock_client = mock.Mock()
  mock_get_ads_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service

  mock_response = mock.Mock()
  mock_response.results = [
      mock.Mock(resource_name="customers/123/adGroupCriteria/kw1"),
      mock.Mock(resource_name="customers/123/adGroupCriteria/kw2"),
  ]
  mock_service.mutate_ad_group_criteria.return_value = mock_response

  result = mutations.create_keywords(
      customer_id="123",
      ad_group_resource_name="customers/123/adGroups/abc",
      keywords=[
          {"text": "keyword1", "match_type": "EXACT"},
          {"text": "keyword2", "match_type": "PHRASE"},
      ],
  )

  assert result == {
      "resource_names": [
          "customers/123/adGroupCriteria/kw1",
          "customers/123/adGroupCriteria/kw2",
      ]
  }
  mock_service.mutate_ad_group_criteria.assert_called_once()


@mock.patch("ads_mcp.tools.mutations.get_ads_client")
def test_create_keywords_failure(mock_get_ads_client):
  """Tests create_keywords handles GoogleAdsException."""
  mock_client = mock.Mock()
  mock_get_ads_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service

  mock_error = mock.Mock()
  mock_error.__str__ = mock.Mock(return_value="Invalid keyword")

  mock_service.mutate_ad_group_criteria.side_effect = MockGoogleAdsException(
      [mock_error]
  )

  with pytest.raises(ToolError) as exc_info:
    mutations.create_keywords(
        customer_id="123",
        ad_group_resource_name="customers/123/adGroups/abc",
        keywords=[{"text": "keyword1", "match_type": "EXACT"}],
    )

  assert "Invalid keyword" in str(exc_info.value)


@mock.patch("ads_mcp.tools.mutations.get_ads_client")
def test_create_negative_campaign_keywords_success(mock_get_ads_client):
  """Tests successful creation of negative campaign keywords."""
  mock_client = mock.Mock()
  mock_get_ads_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service

  mock_response = mock.Mock()
  mock_response.results = [
      mock.Mock(resource_name="customers/123/campaignCriteria/nc1"),
      mock.Mock(resource_name="customers/123/campaignCriteria/nc2"),
  ]
  mock_service.mutate_campaign_criteria.return_value = mock_response

  result = mutations.create_negative_campaign_keywords(
      customer_id="123",
      campaign_resource_name="customers/123/campaigns/789",
      keywords=["free", "fake"],
  )

  assert result == {
      "resource_names": [
          "customers/123/campaignCriteria/nc1",
          "customers/123/campaignCriteria/nc2",
      ]
  }
  mock_service.mutate_campaign_criteria.assert_called_once()


@mock.patch("ads_mcp.tools.mutations.get_ads_client")
def test_create_negative_campaign_keywords_failure(mock_get_ads_client):
  """Tests create_negative_campaign_keywords handles GoogleAdsException."""
  mock_client = mock.Mock()
  mock_get_ads_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service

  mock_error = mock.Mock()
  mock_error.__str__ = mock.Mock(return_value="Invalid negative keyword")

  mock_service.mutate_campaign_criteria.side_effect = MockGoogleAdsException(
      [mock_error]
  )

  with pytest.raises(ToolError) as exc_info:
    mutations.create_negative_campaign_keywords(
        customer_id="123",
        campaign_resource_name="customers/123/campaigns/789",
        keywords=["free"],
    )

  assert "Invalid negative keyword" in str(exc_info.value)


@mock.patch("ads_mcp.tools.mutations.get_ads_client")
def test_create_geo_targeting_success(mock_get_ads_client):
  """Tests create_geo_targeting successfully adds location targeting."""
  mock_client = mock.Mock()
  mock_get_ads_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service
  mock_geo_svc = mock.Mock()
  mock_client.get_service.side_effect = lambda name: {
      "CampaignCriterionService": mock_service,
      "GeoTargetConstantService": mock_geo_svc,
  }[name]

  mock_geo_svc.geo_target_constant_path.side_effect = (
      lambda geo_id: f"geoTargetConstants/{geo_id}"
  )

  mock_response = mock.Mock()
  mock_response.results = [
      mock.Mock(resource_name="customers/123/campaignCriteria/geo1"),
      mock.Mock(resource_name="customers/123/campaignCriteria/geo2"),
  ]
  mock_service.mutate_campaign_criteria.return_value = mock_response

  result = mutations.create_geo_targeting(
      customer_id="123",
      campaign_resource_name="customers/123/campaigns/789",
      geo_target_constant_ids=[2840, 2124],
  )

  assert result == {
      "resource_names": [
          "customers/123/campaignCriteria/geo1",
          "customers/123/campaignCriteria/geo2",
      ]
  }
  mock_service.mutate_campaign_criteria.assert_called_once()


@mock.patch("ads_mcp.tools.mutations.get_ads_client")
def test_create_geo_targeting_failure(mock_get_ads_client):
  """Tests create_geo_targeting handles GoogleAdsException."""
  mock_client = mock.Mock()
  mock_get_ads_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service
  mock_geo_svc = mock.Mock()
  mock_client.get_service.side_effect = lambda name: {
      "CampaignCriterionService": mock_service,
      "GeoTargetConstantService": mock_geo_svc,
  }[name]

  mock_geo_svc.geo_target_constant_path.side_effect = (
      lambda geo_id: f"geoTargetConstants/{geo_id}"
  )

  mock_error = mock.Mock()
  mock_error.__str__ = mock.Mock(return_value="Invalid geo ID")

  mock_service.mutate_campaign_criteria.side_effect = MockGoogleAdsException(
      [mock_error]
  )

  with pytest.raises(ToolError) as exc_info:
    mutations.create_geo_targeting(
        customer_id="123",
        campaign_resource_name="customers/123/campaigns/789",
        geo_target_constant_ids=[2840],
    )

  assert "Invalid geo ID" in str(exc_info.value)


@mock.patch("ads_mcp.tools.mutations.get_ads_client")
def test_remove_campaign_criterion_success(mock_get_ads_client):
  """Tests remove_campaign_criterion successfully removes a criterion."""
  mock_client = mock.Mock()
  mock_get_ads_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service

  mock_service.campaign_criterion_path.return_value = (
      "customers/123/campaignCriteria/789~abc"
  )

  mock_response = mock.Mock()
  mock_response.results = [
      mock.Mock(resource_name="customers/123/campaignCriteria/789~abc")
  ]
  mock_service.mutate_campaign_criteria.return_value = mock_response

  result = mutations.remove_campaign_criterion(
      customer_id="123",
      campaign_id="789",
      criterion_id="abc",
  )

  assert result == {"removed": "customers/123/campaignCriteria/789~abc"}
  mock_service.mutate_campaign_criteria.assert_called_once()


@mock.patch("ads_mcp.tools.mutations.get_ads_client")
def test_remove_campaign_criterion_failure(mock_get_ads_client):
  """Tests remove_campaign_criterion handles GoogleAdsException."""
  mock_client = mock.Mock()
  mock_get_ads_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service

  mock_service.campaign_criterion_path.return_value = (
      "customers/123/campaignCriteria/789~abc"
  )

  mock_error = mock.Mock()
  mock_error.__str__ = mock.Mock(return_value="Criterion not found")

  mock_service.mutate_campaign_criteria.side_effect = MockGoogleAdsException(
      [mock_error]
  )

  with pytest.raises(ToolError) as exc_info:
    mutations.remove_campaign_criterion(
        customer_id="123",
        campaign_id="789",
        criterion_id="abc",
    )

  assert "Criterion not found" in str(exc_info.value)


@mock.patch("ads_mcp.tools.mutations.get_ads_client")
def test_exclude_geo_targets_success(mock_get_ads_client):
  """Tests exclude_geo_targets successfully excludes locations."""
  mock_client = mock.Mock()
  mock_get_ads_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service
  mock_geo_svc = mock.Mock()
  mock_client.get_service.side_effect = lambda name: {
      "CampaignCriterionService": mock_service,
      "GeoTargetConstantService": mock_geo_svc,
  }[name]

  mock_geo_svc.geo_target_constant_path.side_effect = (
      lambda geo_id: f"geoTargetConstants/{geo_id}"
  )

  mock_response = mock.Mock()
  mock_response.results = [
      mock.Mock(resource_name="customers/123/campaignCriteria/geo1"),
      mock.Mock(resource_name="customers/123/campaignCriteria/geo2"),
  ]
  mock_service.mutate_campaign_criteria.return_value = mock_response

  result = mutations.exclude_geo_targets(
      customer_id="123",
      campaign_resource_name="customers/123/campaigns/789",
      geo_target_constant_ids=[2840, 2124],
  )

  assert result == {
      "resource_names": [
          "customers/123/campaignCriteria/geo1",
          "customers/123/campaignCriteria/geo2",
      ]
  }
  mock_service.mutate_campaign_criteria.assert_called_once()


@mock.patch("ads_mcp.tools.mutations.get_ads_client")
def test_exclude_geo_targets_failure(mock_get_ads_client):
  """Tests exclude_geo_targets handles GoogleAdsException."""
  mock_client = mock.Mock()
  mock_get_ads_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service
  mock_geo_svc = mock.Mock()
  mock_client.get_service.side_effect = lambda name: {
      "CampaignCriterionService": mock_service,
      "GeoTargetConstantService": mock_geo_svc,
  }[name]

  mock_geo_svc.geo_target_constant_path.side_effect = (
      lambda geo_id: f"geoTargetConstants/{geo_id}"
  )

  mock_error = mock.Mock()
  mock_error.__str__ = mock.Mock(return_value="Invalid geo ID")

  mock_service.mutate_campaign_criteria.side_effect = MockGoogleAdsException(
      [mock_error]
  )

  with pytest.raises(ToolError) as exc_info:
    mutations.exclude_geo_targets(
        customer_id="123",
        campaign_resource_name="customers/123/campaigns/789",
        geo_target_constant_ids=[2840],
    )

  assert "Invalid geo ID" in str(exc_info.value)


@mock.patch("ads_mcp.tools.mutations.get_ads_client")
def test_update_campaign_status_success(mock_get_ads_client):
  """Tests update_campaign_status successfully updates status."""
  mock_client = mock.Mock()
  mock_get_ads_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service

  mock_response = mock.Mock()
  mock_response.results = [
      mock.Mock(resource_name="customers/123/campaigns/789")
  ]
  mock_service.mutate_campaigns.return_value = mock_response

  result = mutations.update_campaign_status(
      customer_id="123",
      campaign_resource_name="customers/123/campaigns/789",
      status="ENABLED",
  )

  assert result == {"resource_name": "customers/123/campaigns/789"}
  mock_service.mutate_campaigns.assert_called_once()


@mock.patch("ads_mcp.tools.mutations.get_ads_client")
def test_update_campaign_status_failure(mock_get_ads_client):
  """Tests update_campaign_status handles GoogleAdsException."""
  mock_client = mock.Mock()
  mock_get_ads_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service

  mock_error = mock.Mock()
  mock_error.__str__ = mock.Mock(return_value="Campaign not found")

  mock_service.mutate_campaigns.side_effect = MockGoogleAdsException(
      [mock_error]
  )

  with pytest.raises(ToolError) as exc_info:
    mutations.update_campaign_status(
        customer_id="123",
        campaign_resource_name="customers/123/campaigns/789",
        status="ENABLED",
    )

  assert "Campaign not found" in str(exc_info.value)


@mock.patch("ads_mcp.tools.mutations.get_ads_client")
def test_update_ad_group_status_success(mock_get_ads_client):
  """Tests update_ad_group_status successfully updates status."""
  mock_client = mock.Mock()
  mock_get_ads_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service

  mock_response = mock.Mock()
  mock_response.results = [
      mock.Mock(resource_name="customers/123/adGroups/abc")
  ]
  mock_service.mutate_ad_groups.return_value = mock_response

  result = mutations.update_ad_group_status(
      customer_id="123",
      ad_group_resource_name="customers/123/adGroups/abc",
      status="PAUSED",
  )

  assert result == {"resource_name": "customers/123/adGroups/abc"}
  mock_service.mutate_ad_groups.assert_called_once()


@mock.patch("ads_mcp.tools.mutations.get_ads_client")
def test_update_ad_group_status_failure(mock_get_ads_client):
  """Tests update_ad_group_status handles GoogleAdsException."""
  mock_client = mock.Mock()
  mock_get_ads_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service

  mock_error = mock.Mock()
  mock_error.__str__ = mock.Mock(return_value="Ad group not found")

  mock_service.mutate_ad_groups.side_effect = MockGoogleAdsException(
      [mock_error]
  )

  with pytest.raises(ToolError) as exc_info:
    mutations.update_ad_group_status(
        customer_id="123",
        ad_group_resource_name="customers/123/adGroups/abc",
        status="PAUSED",
    )

  assert "Ad group not found" in str(exc_info.value)


@mock.patch("ads_mcp.tools.mutations.get_ads_client")
def test_update_campaign_geo_target_type_success(mock_get_ads_client):
  """Tests update_campaign_geo_target_type successfully updates."""
  mock_client = mock.Mock()
  mock_get_ads_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service

  mock_response = mock.Mock()
  mock_response.results = [
      mock.Mock(resource_name="customers/123/campaigns/789")
  ]
  mock_service.mutate_campaigns.return_value = mock_response

  result = mutations.update_campaign_geo_target_type(
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
    mutations.update_campaign_geo_target_type(
        customer_id="123",
        campaign_resource_name="customers/123/campaigns/789",
    )
  assert "At least one of" in str(exc_info.value)


@mock.patch("ads_mcp.tools.mutations.get_ads_client")
def test_update_campaign_geo_target_type_failure(mock_get_ads_client):
  """Tests update_campaign_geo_target_type handles GoogleAdsException."""
  mock_client = mock.Mock()
  mock_get_ads_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service

  mock_error = mock.Mock()
  mock_error.__str__ = mock.Mock(return_value="Campaign not found")

  mock_service.mutate_campaigns.side_effect = MockGoogleAdsException(
      [mock_error]
  )

  with pytest.raises(ToolError) as exc_info:
    mutations.update_campaign_geo_target_type(
        customer_id="123",
        campaign_resource_name="customers/123/campaigns/789",
        positive_geo_target_type="PRESENCE",
    )

  assert "Campaign not found" in str(exc_info.value)
