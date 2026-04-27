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

"""Tests for common mutation utilities."""

from ads_mcp.tools._ads_api import enum_types
from ads_mcp.tools.mutations import common
from fastmcp.exceptions import ToolError
import pytest

# pylint: disable=protected-access


def test_resolve_enum_success():
  """Tests _resolve_enum with valid input."""
  enum_type = enum_types.BudgetDeliveryMethodEnum.BudgetDeliveryMethod
  result = common._resolve_enum(enum_type, "STANDARD", "delivery_method")
  assert result == enum_type.STANDARD


def test_resolve_enum_case_insensitive():
  """Tests _resolve_enum with case-insensitive input."""
  enum_type = enum_types.BudgetDeliveryMethodEnum.BudgetDeliveryMethod
  result = common._resolve_enum(enum_type, "standard", "delivery_method")
  assert result == enum_type.STANDARD


def test_resolve_enum_invalid():
  """Tests _resolve_enum with invalid input."""
  enum_type = enum_types.BudgetDeliveryMethodEnum.BudgetDeliveryMethod
  with pytest.raises(ToolError) as exc_info:
    common._resolve_enum(enum_type, "INVALID_VALUE", "delivery_method")
  assert "Invalid delivery_method" in str(exc_info.value)
  assert "STANDARD" in str(exc_info.value)
