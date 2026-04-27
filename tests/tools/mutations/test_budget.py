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

"""Tests for budget mutation tools."""

from unittest import mock
from ads_mcp.tools.mutations import budget
from fastmcp.exceptions import ToolError
from google.ads.googleads.errors import GoogleAdsException
import pytest


class MockGoogleAdsException(GoogleAdsException):
  """Mock GoogleAdsException for testing."""

  def __init__(self, errors):  # pylint: disable=super-init-not-called
    self.failure = mock.Mock()
    self.failure.errors = errors


@mock.patch("ads_mcp.tools.mutations.budget._get_client")
def test_create_campaign_budget_success(mock_get_client):
  """Tests create_campaign_budget successfully creates a budget."""
  mock_client = mock.Mock()
  mock_get_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service

  mock_response = mock.Mock()
  mock_response.results = [
      mock.Mock(resource_name="customers/123/campaignBudgets/456")
  ]
  mock_service.mutate_campaign_budgets.return_value = mock_response

  result = budget.create_campaign_budget(
      customer_id="123",
      name="Test Budget",
      amount_micros=1000000,
  )

  assert result == {"resource_name": "customers/123/campaignBudgets/456"}
  mock_service.mutate_campaign_budgets.assert_called_once()


@mock.patch("ads_mcp.tools.mutations.budget._get_client")
def test_create_campaign_budget_failure(mock_get_client):
  """Tests create_campaign_budget handles GoogleAdsException."""
  mock_client = mock.Mock()
  mock_get_client.return_value = mock_client
  mock_service = mock.Mock()
  mock_client.get_service.return_value = mock_service

  mock_error = mock.Mock()
  mock_error.__str__ = mock.Mock(return_value="Invalid budget name")

  mock_service.mutate_campaign_budgets.side_effect = MockGoogleAdsException(
      [mock_error]
  )

  with pytest.raises(ToolError) as exc_info:
    budget.create_campaign_budget(
        customer_id="123",
        name="Test Budget",
        amount_micros=1000000,
    )

  assert "Invalid budget name" in str(exc_info.value)
