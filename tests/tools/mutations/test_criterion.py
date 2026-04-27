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

"""Tests for criterion mutation tools."""

from unittest import mock
from ads_mcp.tools.mutations import criterion
from fastmcp.exceptions import ToolError
from google.ads.googleads.errors import GoogleAdsException
import pytest


class MockGoogleAdsException(GoogleAdsException):
  """Mock GoogleAdsException for testing."""

  def __init__(self, errors):  # pylint: disable=super-init-not-called
    self.failure = mock.Mock()
    self.failure.errors = errors


@mock.patch("ads_mcp.tools.mutations.criterion._get_client")
def test_create_keywords_success(mock_get_client):
  """Tests create_keywords successfully creates keywords."""
  mock_client = mock.Mock()
  mock_get_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service

  mock_response = mock.Mock()
  mock_response.results = [
      mock.Mock(resource_name="customers/123/adGroupCriteria/kw1"),
      mock.Mock(resource_name="customers/123/adGroupCriteria/kw2"),
  ]
  mock_service.mutate_ad_group_criteria.return_value = mock_response

  result = criterion.create_keywords(
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


@mock.patch("ads_mcp.tools.mutations.criterion._get_client")
def test_create_keywords_failure(mock_get_client):
  """Tests create_keywords handles GoogleAdsException."""
  mock_client = mock.Mock()
  mock_get_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service

  mock_error = mock.Mock()
  mock_error.__str__ = mock.Mock(return_value="Invalid keyword")

  mock_service.mutate_ad_group_criteria.side_effect = MockGoogleAdsException(
      [mock_error]
  )

  with pytest.raises(ToolError) as exc_info:
    criterion.create_keywords(
        customer_id="123",
        ad_group_resource_name="customers/123/adGroups/abc",
        keywords=[{"text": "keyword1", "match_type": "EXACT"}],
    )

  assert "Invalid keyword" in str(exc_info.value)


@mock.patch("ads_mcp.tools.mutations.criterion._get_client")
def test_create_negative_campaign_keywords_success(mock_get_client):
  """Tests successful creation of negative campaign keywords."""
  mock_client = mock.Mock()
  mock_get_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service

  mock_response = mock.Mock()
  mock_response.results = [
      mock.Mock(resource_name="customers/123/campaignCriteria/nc1"),
      mock.Mock(resource_name="customers/123/campaignCriteria/nc2"),
  ]
  mock_service.mutate_campaign_criteria.return_value = mock_response

  result = criterion.create_negative_campaign_keywords(
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


@mock.patch("ads_mcp.tools.mutations.criterion._get_client")
def test_create_negative_campaign_keywords_failure(mock_get_client):
  """Tests create_negative_campaign_keywords handles GoogleAdsException."""
  mock_client = mock.Mock()
  mock_get_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service

  mock_error = mock.Mock()
  mock_error.__str__ = mock.Mock(return_value="Invalid negative keyword")

  mock_service.mutate_campaign_criteria.side_effect = MockGoogleAdsException(
      [mock_error]
  )

  with pytest.raises(ToolError) as exc_info:
    criterion.create_negative_campaign_keywords(
        customer_id="123",
        campaign_resource_name="customers/123/campaigns/789",
        keywords=["free"],
    )

  assert "Invalid negative keyword" in str(exc_info.value)


@mock.patch("ads_mcp.tools.mutations.criterion._get_client")
def test_create_geo_targeting_success(mock_get_client):
  """Tests create_geo_targeting successfully adds location targeting."""
  mock_client = mock.Mock()
  mock_get_client.return_value = mock_client
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

  result = criterion.create_geo_targeting(
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


@mock.patch("ads_mcp.tools.mutations.criterion._get_client")
def test_create_geo_targeting_failure(mock_get_client):
  """Tests create_geo_targeting handles GoogleAdsException."""
  mock_client = mock.Mock()
  mock_get_client.return_value = mock_client
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
    criterion.create_geo_targeting(
        customer_id="123",
        campaign_resource_name="customers/123/campaigns/789",
        geo_target_constant_ids=[2840],
    )

  assert "Invalid geo ID" in str(exc_info.value)


@mock.patch("ads_mcp.tools.mutations.criterion._get_client")
def test_remove_campaign_criterion_success(mock_get_client):
  """Tests remove_campaign_criterion successfully removes a criterion."""
  mock_client = mock.Mock()
  mock_get_client.return_value = mock_client
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

  result = criterion.remove_campaign_criterion(
      customer_id="123",
      campaign_id="789",
      criterion_id="abc",
  )

  assert result == {"removed": "customers/123/campaignCriteria/789~abc"}
  mock_service.mutate_campaign_criteria.assert_called_once()


@mock.patch("ads_mcp.tools.mutations.criterion._get_client")
def test_remove_campaign_criterion_failure(mock_get_client):
  """Tests remove_campaign_criterion handles GoogleAdsException."""
  mock_client = mock.Mock()
  mock_get_client.return_value = mock_client
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
    criterion.remove_campaign_criterion(
        customer_id="123",
        campaign_id="789",
        criterion_id="abc",
    )

  assert "Criterion not found" in str(exc_info.value)


@mock.patch("ads_mcp.tools.mutations.criterion._get_client")
def test_exclude_geo_targets_success(mock_get_client):
  """Tests exclude_geo_targets successfully excludes locations."""
  mock_client = mock.Mock()
  mock_get_client.return_value = mock_client
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

  result = criterion.exclude_geo_targets(
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


@mock.patch("ads_mcp.tools.mutations.criterion._get_client")
def test_exclude_geo_targets_failure(mock_get_client):
  """Tests exclude_geo_targets handles GoogleAdsException."""
  mock_client = mock.Mock()
  mock_get_client.return_value = mock_client
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
    criterion.exclude_geo_targets(
        customer_id="123",
        campaign_resource_name="customers/123/campaigns/789",
        geo_target_constant_ids=[2840],
    )

  assert "Invalid geo ID" in str(exc_info.value)
