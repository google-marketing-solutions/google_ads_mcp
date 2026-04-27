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

"""Common utilities for Google Ads API MCP tools."""

import os
from ads_mcp.utils import ROOT_DIR
from fastmcp.server.dependencies import get_access_token
from google.ads.googleads.client import GoogleAdsClient
from google.oauth2.credentials import Credentials
import yaml

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
        credentials,
        developer_token=ads_config.get("developer_token"),
        use_proto_plus=True,
    )

  if not _ADS_CLIENT:
    _ADS_CLIENT = GoogleAdsClient.load_from_storage(credentials_path)
    _ADS_CLIENT.use_proto_plus = (
        True  # Forced enable proto plus to avoid attribute issues.
    )

  return _ADS_CLIENT
