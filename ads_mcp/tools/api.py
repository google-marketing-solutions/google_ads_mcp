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
import sys
import json
from typing import Any

from ads_mcp.utils import ROOT_DIR
from ads_mcp.oauth_client import oauth_client
from ads_mcp.coordinator import mcp_server

from fastmcp.server.dependencies import get_access_token, get_http_headers
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.util import get_nested_attr
from google.ads.googleads.v21.services.services.customer_service import CustomerServiceClient
from google.ads.googleads.v21.services.services.google_ads_service import GoogleAdsServiceClient
from google.oauth2.credentials import Credentials
import proto
import yaml

_ADS_CLIENT: GoogleAdsClient | None = None


def get_refresh_token_from_headers() -> str | None:
  """Extracts refresh token from HTTP request headers.
  
  Checks for X-OAuth-Refresh-Token header from the HTTP request.
  
  Returns:
      Refresh token string if found, None otherwise.
  """
  try:
    headers = get_http_headers()
    if headers:
      # FastMCP provides headers as dict
      return headers.get('x-oauth-refresh-token') or headers.get('X-OAuth-Refresh-Token')
  except Exception:
    pass
  return None


def get_ads_client(access_token: str = None) -> GoogleAdsClient:
  """Gets a GoogleAdsClient instance.

  Args:
      access_token: Optional access token to use directly.

  Tries multiple authentication methods in order:
  1. Provided access_token parameter
  2. Dynamic OAuth client (external API)
  3. FastMCP access token
  4. YAML file credentials

  Returns:
      A GoogleAdsClient instance.

  Raises:
      FileNotFoundError: If the credentials YAML file is not found.
  """
  global _ADS_CLIENT

  # Método 1: Usa access_token fornecido diretamente
  if access_token:
    default_path = f"{ROOT_DIR}/google-ads.yaml"
    credentials_path = os.environ.get("GOOGLE_ADS_CREDENTIALS", default_path)
    
    if os.path.isfile(credentials_path):
      credentials = Credentials(access_token)
      with open(credentials_path, "r", encoding="utf-8") as f:
        ads_config = yaml.safe_load(f.read())
      return GoogleAdsClient(
          credentials, developer_token=ads_config.get("developer_token")
      )

  # Método 2: Tenta OAuth dinâmico
  dynamic_token = oauth_client.get_access_token()
  if dynamic_token:
    default_path = f"{ROOT_DIR}/google-ads.yaml"
    credentials_path = os.environ.get("GOOGLE_ADS_CREDENTIALS", default_path)
    
    if os.path.isfile(credentials_path):
      credentials = Credentials(dynamic_token)
      with open(credentials_path, "r", encoding="utf-8") as f:
        ads_config = yaml.safe_load(f.read())
      return GoogleAdsClient(
          credentials, developer_token=ads_config.get("developer_token")
      )

  # Método 2: FastMCP access token
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

  # Método 3: YAML file (fallback)
  if not _ADS_CLIENT:
    _ADS_CLIENT = GoogleAdsClient.load_from_storage(credentials_path)

  return _ADS_CLIENT


@mcp_server.tool()
def list_accessible_accounts() -> list[str]:
  """Lists Google Ads customers id directly accessible by the user.

  Authentication is provided via X-OAuth-Refresh-Token header.

  Returns:
      List of customer IDs that can be used as `login_customer_id`.
  """
  # Get refresh_token from HTTP headers (ADK passes it via StreamableHTTPConnectionParams)
  refresh_token = get_refresh_token_from_headers()
  if not refresh_token:
    raise Exception("Missing X-OAuth-Refresh-Token header for authentication")
  
  # Generate access_token from client's refresh_token
  access_token = oauth_client._generate_access_token_from_refresh(refresh_token)
  if not access_token:
    raise Exception("Failed to generate access token from refresh token")
  
  ads_client = get_ads_client(access_token)
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
  try:
    if isinstance(value, proto.Message):
      return_value = proto.Message.to_dict(value)
    elif isinstance(value, proto.Enum):
      # Try to get the name, fallback to number if attribute error
      try:
        return_value = value.name
      except AttributeError:
        return_value = int(value)
    else:
      return_value = value
    return return_value
  except Exception as e:
    print(f"DEBUG: format_value error for value {value}: {e}", file=sys.stderr)
    # Return the raw value if formatting fails
    return value


@mcp_server.tool()
def execute_gaql(
    query: str,
    customer_id: str,
    login_customer_id: str | None = None,
) -> list[dict[str, Any]]:
  """Executes a Google Ads Query Language (GAQL) query to get reporting data.

  Authentication is provided via X-OAuth-Refresh-Token header.

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
  
  # Get refresh_token from HTTP headers (ADK passes it via StreamableHTTPConnectionParams)
  refresh_token = get_refresh_token_from_headers()
  if not refresh_token:
    raise Exception("Missing X-OAuth-Refresh-Token header for authentication")
  
  # Generate access_token from client's refresh_token
  access_token = oauth_client._generate_access_token_from_refresh(refresh_token)
  if not access_token:
    raise Exception("Failed to generate access token from refresh token")
  
  ads_client = get_ads_client(access_token)
  if login_customer_id:
    ads_client.login_customer_id = login_customer_id
  ads_service: GoogleAdsServiceClient = ads_client.get_service(
      "GoogleAdsService"
  )
  try:
    print(f"DEBUG: Executing query for customer {customer_id}", file=sys.stderr)
    query_res = ads_service.search_stream(query=query, customer_id=customer_id)
    output = []
    for batch in query_res:
      print(f"DEBUG: Processing batch with {len(batch.results)} results", file=sys.stderr)
      for row in batch.results:
        # Use field_mask.paths to get only the fields requested in the SELECT
        # This avoids complex nested objects like Campaign
        row_data = {}
        for field_path in batch.field_mask.paths:
          try:
            # Python SDK uses underscores for reserved keywords (e.g., type -> type_)
            # Transform field path for Python object access
            python_field_path = field_path.replace('.type', '.type_')
            
            raw_value = get_nested_attr(row, python_field_path)
            formatted_value = format_value(raw_value)
            
            # Use original field_path (without underscore) as key for JSON output
            row_data[field_path] = formatted_value
          except Exception as e:
            print(f"DEBUG: Error processing field {field_path}: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            raise
        output.append(row_data)
    
    # Debug logging to verify serialization works
    if output:
      try:
        sample = json.dumps(output[0])
        print(f"DEBUG: Successfully formatted first row: {sample[:200]}", file=sys.stderr)
      except Exception as e:
        print(f"DEBUG: JSON serialization failed: {e}", file=sys.stderr)
    
    return output
  except GoogleAdsException as e:
    # Handle Google Ads API errors from the failure object
    error_details = []
    for error in e.failure.errors:
      error_details.append(f"Error: {error.message}")
      try:
        error_details.append(f"  Location: {error.location}")
      except AttributeError:
        pass
      try:
        error_details.append(f"  Error Code: {error.error_code}")
      except AttributeError:
        pass
      try:
        if hasattr(error, 'trigger') and error.trigger:
          error_details.append(f"  Trigger: {error.trigger}")
      except AttributeError:
        pass
    
    full_error = "\n".join(error_details) if error_details else str(e.failure.errors)
    print(f"DEBUG: Full Google Ads API error: {full_error}", file=sys.stderr)
    raise RuntimeError(full_error) from e


