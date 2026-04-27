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

"""Ad mutation tools for Google Ads API."""

from ads_mcp.coordinator import mcp_server as mcp
from ads_mcp.tools._ads_api import common_types
from ads_mcp.tools._ads_api import enum_types
from ads_mcp.tools._ads_api import resource_types
from ads_mcp.tools._ads_api import service_types
from ads_mcp.tools.mutations.common import _get_client
from ads_mcp.tools.mutations.common import _handle_google_ads_error
from ads_mcp.tools.mutations.common import _resolve_enum
from google.ads.googleads.errors import GoogleAdsException


@mcp.tool()
def create_responsive_search_ad(
    customer_id: str,
    ad_group_resource_name: str,
    headlines: list[str],
    descriptions: list[str],
    final_url: str,
    path1: str = "",
    path2: str = "",
    status: str = "ENABLED",
    login_customer_id: str | None = None,
) -> dict[str, str]:
  """Creates a Responsive Search Ad in an ad group.

  Args:
      customer_id: Google Ads customer ID (digits only).
      ad_group_resource_name: Resource name from create_ad_group.
      headlines: List of headline strings (3-15 headlines, max 30 chars).
      descriptions: List of description strings (2-4, max 90 chars).
      final_url: Landing page URL.
      path1: Display URL path1 (max 15 chars, optional).
      path2: Display URL path2 (max 15 chars, optional).
      status: ENABLED or PAUSED. Default ENABLED.
      login_customer_id: MCC account ID if customer is managed.

  Returns:
      Dict with the ad_group_ad resource_name.
  """
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("AdGroupAdService")

  headline_assets = [common_types.AdTextAsset(text=h) for h in headlines]
  description_assets = [common_types.AdTextAsset(text=d) for d in descriptions]

  rsa_info = common_types.ResponsiveSearchAdInfo(
      headlines=headline_assets,
      descriptions=description_assets,
  )
  if path1:
    rsa_info.path1 = path1
  if path2:
    rsa_info.path2 = path2

  ad = resource_types.Ad(
      final_urls=[final_url],
      responsive_search_ad=rsa_info,
  )

  ad_group_ad = resource_types.AdGroupAd(
      ad_group=ad_group_resource_name,
      status=_resolve_enum(
          enum_types.AdGroupAdStatusEnum.AdGroupAdStatus, status, "status"
      ),
      ad=ad,
  )

  operation = service_types.AdGroupAdOperation(create=ad_group_ad)
  try:
    response = service.mutate_ad_group_ads(
        customer_id=customer_id, operations=[operation]
    )
  except GoogleAdsException as e:
    _handle_google_ads_error(e)

  resource_name = response.results[0].resource_name
  return {"resource_name": resource_name}
