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

"""This module contains tools for interacting with the Google Ads API."""

import os
from typing import Any
import json

from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import get_access_token
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.util import get_nested_attr
from google.ads.googleads.v22.services.services.customer_service import CustomerServiceClient
from google.ads.googleads.v22.services.services.google_ads_service import GoogleAdsServiceClient
from google.oauth2.credentials import Credentials
import proto
import yaml

from ads_mcp.coordinator import mcp_server as mcp
from ads_mcp.utils import ROOT_DIR


_ADS_CLIENT: GoogleAdsClient | None = None


def get_ads_client() -> GoogleAdsClient:
  """Gets a GoogleAdsClient instance.

  Looks for an access token from the environment or loads credentials from
  a YAML file.

  Returns:
      A GoogleAdsClient instance.

  Raises:
      FileNotFoundError: If the credentials YAML file is not found.
  """
  global _ADS_CLIENT

  access_token = get_access_token()
  if access_token:
    access_token = access_token.token

  default_path = f"{ROOT_DIR}/google-ads.yaml"
  credentials_path = os.environ.get("GOOGLE_ADS_CREDENTIALS", default_path)
  if not os.path.isfile(credentials_path):
    raise FileNotFoundError(
        "Google Ads credentials YAML file is not found. "
        "Check [GOOGLE_ADS_CREDENTIALS] config."
    )

  if access_token:
    credentials = Credentials(access_token)
    with open(credentials_path, "r", encoding="utf-8") as f:
      ads_config = yaml.safe_load(f.read())
    return GoogleAdsClient(
        credentials, developer_token=ads_config.get("developer_token")
    )

  if not _ADS_CLIENT:
    _ADS_CLIENT = GoogleAdsClient.load_from_storage(credentials_path)

  return _ADS_CLIENT


@mcp.tool()
def list_accessible_accounts() -> list[str]:
  """Lists Google Ads customers id directly accessible by the user.

  The accounts can be used as `login_customer_id`.
  """
  ads_client = get_ads_client()
  customer_service: CustomerServiceClient = ads_client.get_service(
      "CustomerService"
  )
  accounts = customer_service.list_accessible_customers().resource_names
  return [account.split("/")[-1] for account in accounts]


def preprocess_gaql(query: str) -> str:
  """Preprocesses a GAQL query to add omit_unselected_resource_names=true."""
  if "omit_unselected_resource_names" not in query:
    if "PARAMETERS" in query and "include_drafts" in query:
      return query + " omit_unselected_resource_names=true"
    return query + " PARAMETERS omit_unselected_resource_names=true"
  return query


def format_value(value: Any) -> Any:
  """Formats a value from a Google Ads API response."""
  if isinstance(value, proto.marshal.collections.repeated.Repeated):
    return_value = [format_value(i) for i in value]
  elif isinstance(value, proto.Message):
    # covert to json first to avoid serialization issues
    return_value = proto.Message.to_json(
        value,
        use_integers_for_enums=False,
    )
    return_value = json.loads(return_value)
  elif isinstance(value, proto.Enum):
    return_value = value.name
  else:
    return_value = value

  return return_value


@mcp.tool(
    output_schema={
        "type": "object",
        "properties": {
            "data": {"type": "array", "items": {"type": "object"}},
        },
        "required": ["data"],
    }
)
def execute_gaql(
    query: str,
    customer_id: str,
    login_customer_id: str | None = None,
) -> list[dict[str, Any]]:
  """Executes a Google Ads Query Language (GAQL) query to get reporting data.

  Args:
      query: The GAQL query to execute.
      customer_id: The ID of the customer being queried. It is only digits.
      login_customer_id: (Optional) The ID of the customer being logged in.
          Usually, it is the MCC on top of the target customer account.
          It is only digits.
          In most cases, a default account is set, it could be optional.

  Returns:
      An array of object, each object representing a row of the query results.
  """
  query = preprocess_gaql(query)
  ads_client = get_ads_client()
  if login_customer_id:
    ads_client.login_customer_id = login_customer_id
  ads_service: GoogleAdsServiceClient = ads_client.get_service(
      "GoogleAdsService"
  )
  try:
    query_res = ads_service.search_stream(query=query, customer_id=customer_id)
    output = []
    for batch in query_res:
      for row in batch.results:
        output.append(
            {
                i: format_value(get_nested_attr(row, i))
                for i in batch.field_mask.paths
            }
        )
  except GoogleAdsException as e:
    raise ToolError("\n".join(str(i) for i in e.failure.errors)) from e

  return {"data": output}
