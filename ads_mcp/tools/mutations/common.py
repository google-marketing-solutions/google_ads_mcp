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

"""Common utilities for mutation tools."""

from ads_mcp.tools._utils import get_ads_client
from fastmcp.exceptions import ToolError
from google.ads.googleads.errors import GoogleAdsException


def _handle_google_ads_error(e: GoogleAdsException) -> None:
  """Raises a ToolError from a GoogleAdsException."""
  raise ToolError("\n".join(str(err) for err in e.failure.errors)) from e


def _get_client(login_customer_id: str | None = None):
  """Gets a GoogleAdsClient, optionally overriding login_customer_id."""
  ads_client = get_ads_client()
  if login_customer_id:
    ads_client.login_customer_id = login_customer_id
  return ads_client


def _resolve_enum(enum_type, value: str, param_name: str):
  """Resolves a proto enum from a case-insensitive string.

  Args:
    enum_type: The proto enum type.
    value: The string value to resolve.
    param_name: The name of the parameter for error messages.

  Returns:
    The resolved enum value.

  Raises:
    ToolError: When the input does not match a member of the enum, listing the
      valid values.
  """
  try:
    return enum_type[value.upper()]
  except (KeyError, AttributeError) as e:
    valid = [
        n for n in enum_type.__members__ if n not in ("UNSPECIFIED", "UNKNOWN")
    ]
    valid_str = ", ".join(valid)
    raise ToolError(
        f"Invalid {param_name}: {value!r}. Valid values: {valid_str}."
    ) from e
