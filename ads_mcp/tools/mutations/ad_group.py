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

"""Ad group mutation tools for Google Ads API."""

from ads_mcp.coordinator import mcp_server as mcp
from ads_mcp.tools._ads_api import enum_types
from ads_mcp.tools._ads_api import resource_types
from ads_mcp.tools._ads_api import service_types
from ads_mcp.tools.mutations.common import _get_client
from ads_mcp.tools.mutations.common import _handle_google_ads_error
from ads_mcp.tools.mutations.common import _resolve_enum
from google.ads.googleads.errors import GoogleAdsException
from google.protobuf import field_mask_pb2


@mcp.tool()
def create_ad_group(
    customer_id: str,
    name: str,
    campaign_resource_name: str,
    cpc_bid_micros: int = 1000000,
    status: str = "ENABLED",
    login_customer_id: str | None = None,
) -> dict[str, str]:
  """Creates an ad group within a campaign.

  Args:
      customer_id: Google Ads customer ID (digits only).
      name: Ad group name (e.g., "S.S. John Barry Shipwreck").
      campaign_resource_name: Resource name from create_search_campaign.
      cpc_bid_micros: Max CPC bid in micros (1000000 = $1.00).
      status: ENABLED or PAUSED. Default ENABLED.
      login_customer_id: MCC account ID if customer is managed.

  Returns:
      Dict with the ad_group resource_name.
  """
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("AdGroupService")

  ad_group = resource_types.AdGroup(
      name=name,
      campaign=campaign_resource_name,
      status=_resolve_enum(
          enum_types.AdGroupStatusEnum.AdGroupStatus, status, "status"
      ),
      type_=enum_types.AdGroupTypeEnum.AdGroupType.SEARCH_STANDARD,
      cpc_bid_micros=cpc_bid_micros,
  )

  operation = service_types.AdGroupOperation(create=ad_group)
  try:
    response = service.mutate_ad_groups(
        customer_id=customer_id, operations=[operation]
    )
  except GoogleAdsException as e:
    _handle_google_ads_error(e)

  resource_name = response.results[0].resource_name
  return {"resource_name": resource_name}


@mcp.tool()
def update_ad_group_status(
    customer_id: str,
    ad_group_resource_name: str,
    status: str,
    login_customer_id: str | None = None,
) -> dict[str, str]:
  """Updates an ad group's status.

  Args:
      customer_id: Google Ads customer ID (digits only).
      ad_group_resource_name: Full resource name of the ad group.
      status: New status: ENABLED or PAUSED.
      login_customer_id: MCC account ID if customer is managed.

  Returns:
      Dict with the updated ad group resource_name.
  """
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("AdGroupService")

  ad_group = resource_types.AdGroup(
      resource_name=ad_group_resource_name,
      status=_resolve_enum(
          enum_types.AdGroupStatusEnum.AdGroupStatus, status, "status"
      ),
  )

  operation = service_types.AdGroupOperation(update=ad_group)
  operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["status"]))

  try:
    response = service.mutate_ad_groups(
        customer_id=customer_id, operations=[operation]
    )
  except GoogleAdsException as e:
    _handle_google_ads_error(e)

  return {"resource_name": response.results[0].resource_name}
