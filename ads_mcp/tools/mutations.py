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

"""Campaign creation and mutation tools for Google Ads API."""

from typing import Any

from fastmcp.exceptions import ToolError
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v23.common.types.ad_asset import AdTextAsset
from google.ads.googleads.v23.common.types.ad_type_infos import (
    ResponsiveSearchAdInfo,
)
from google.ads.googleads.v23.common.types.bidding import TargetSpend
from google.ads.googleads.v23.common.types.criteria import (
    KeywordInfo,
    LocationInfo,
)
from google.ads.googleads.v23.enums.types.ad_group_ad_status import (
    AdGroupAdStatusEnum,
)
from google.ads.googleads.v23.enums.types.ad_group_criterion_status import (
    AdGroupCriterionStatusEnum,
)
from google.ads.googleads.v23.enums.types.ad_group_status import (
    AdGroupStatusEnum,
)
from google.ads.googleads.v23.enums.types.ad_group_type import (
    AdGroupTypeEnum,
)
from google.ads.googleads.v23.enums.types.advertising_channel_type import (
    AdvertisingChannelTypeEnum,
)
from google.ads.googleads.v23.enums.types.budget_delivery_method import (
    BudgetDeliveryMethodEnum,
)
from google.ads.googleads.v23.enums.types.campaign_status import (
    CampaignStatusEnum,
)
from google.ads.googleads.v23.enums.types.eu_political_advertising_status import (
    EuPoliticalAdvertisingStatusEnum,
)
from google.ads.googleads.v23.enums.types.keyword_match_type import (
    KeywordMatchTypeEnum,
)
from google.ads.googleads.v23.resources.types.ad import Ad
from google.ads.googleads.v23.resources.types.ad_group import AdGroup
from google.ads.googleads.v23.resources.types.ad_group_ad import AdGroupAd
from google.ads.googleads.v23.resources.types.ad_group_criterion import (
    AdGroupCriterion,
)
from google.ads.googleads.v23.resources.types.campaign import Campaign
from google.ads.googleads.v23.resources.types.campaign_budget import (
    CampaignBudget,
)
from google.ads.googleads.v23.resources.types.campaign_criterion import (
    CampaignCriterion,
)
from google.ads.googleads.v23.services.types.ad_group_ad_service import (
    AdGroupAdOperation,
)
from google.ads.googleads.v23.services.types.ad_group_criterion_service import (
    AdGroupCriterionOperation,
)
from google.ads.googleads.v23.services.types.ad_group_service import (
    AdGroupOperation,
)
from google.ads.googleads.v23.services.types.campaign_budget_service import (
    CampaignBudgetOperation,
)
from google.ads.googleads.v23.services.types.campaign_criterion_service import (
    CampaignCriterionOperation,
)
from google.ads.googleads.v23.services.types.campaign_service import (
    CampaignOperation,
)

from ads_mcp.coordinator import mcp_server as mcp
from ads_mcp.tools.api import get_ads_client


def _handle_google_ads_error(e: GoogleAdsException) -> None:
  """Raises a ToolError from a GoogleAdsException."""
  raise ToolError(
      "\n".join(str(err) for err in e.failure.errors)
  ) from e


def _get_client(login_customer_id: str | None = None):
  """Gets a GoogleAdsClient, optionally overriding login_customer_id."""
  ads_client = get_ads_client()
  if login_customer_id:
    ads_client.login_customer_id = login_customer_id
  return ads_client


@mcp.tool()
def create_campaign_budget(
    customer_id: str,
    name: str,
    amount_micros: int,
    delivery_method: str = "STANDARD",
    login_customer_id: str | None = None,
) -> dict[str, str]:
  """Creates a campaign budget.

  Args:
      customer_id: Google Ads customer ID (digits only).
      name: Name for the budget (e.g., "MattsCoinage Daily Budget").
      amount_micros: Daily budget in micros (e.g., 4000000 = $4.00).
      delivery_method: STANDARD or ACCELERATED. Default STANDARD.
      login_customer_id: MCC account ID if customer is managed.

  Returns:
      Dict with the budget resource_name.
  """
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("CampaignBudgetService")

  budget = CampaignBudget(
      name=name,
      amount_micros=amount_micros,
      delivery_method=BudgetDeliveryMethodEnum.BudgetDeliveryMethod[
          delivery_method
      ],
  )

  operation = CampaignBudgetOperation(create=budget)
  try:
    response = service.mutate_campaign_budgets(
        customer_id=customer_id, operations=[operation]
    )
  except GoogleAdsException as e:
    _handle_google_ads_error(e)

  resource_name = response.results[0].resource_name
  return {"resource_name": resource_name}


@mcp.tool()
def create_search_campaign(
    customer_id: str,
    name: str,
    budget_resource_name: str,
    status: str = "PAUSED",
    target_google_search: bool = True,
    target_search_network: bool = False,
    target_content_network: bool = False,
    login_customer_id: str | None = None,
) -> dict[str, str]:
  """Creates a Search campaign with TargetSpend bidding.

  Args:
      customer_id: Google Ads customer ID (digits only).
      name: Campaign name (e.g., "MattsCoinage - Collectible Silver").
      budget_resource_name: Resource name from create_campaign_budget.
      status: PAUSED or ENABLED. Default PAUSED.
      target_google_search: Show on Google Search. Default True.
      target_search_network: Show on search partners. Default False.
      target_content_network: Show on Display Network. Default False.
      login_customer_id: MCC account ID if customer is managed.

  Returns:
      Dict with the campaign resource_name.
  """
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("CampaignService")

  eu_status = (
      EuPoliticalAdvertisingStatusEnum
      .EuPoliticalAdvertisingStatus
      .DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING
  )
  campaign = Campaign(
      name=name,
      campaign_budget=budget_resource_name,
      status=CampaignStatusEnum.CampaignStatus[status],
      advertising_channel_type=(
          AdvertisingChannelTypeEnum.AdvertisingChannelType.SEARCH
      ),
      target_spend=TargetSpend(),
      contains_eu_political_advertising=eu_status,
  )
  campaign.network_settings.target_google_search = target_google_search
  campaign.network_settings.target_search_network = (
      target_search_network
  )
  campaign.network_settings.target_content_network = (
      target_content_network
  )
  campaign.network_settings.target_partner_search_network = False

  operation = CampaignOperation(create=campaign)
  try:
    response = service.mutate_campaigns(
        customer_id=customer_id, operations=[operation]
    )
  except GoogleAdsException as e:
    _handle_google_ads_error(e)

  resource_name = response.results[0].resource_name
  return {"resource_name": resource_name}


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

  ad_group = AdGroup(
      name=name,
      campaign=campaign_resource_name,
      status=AdGroupStatusEnum.AdGroupStatus[status],
      type_=AdGroupTypeEnum.AdGroupType.SEARCH_STANDARD,
      cpc_bid_micros=cpc_bid_micros,
  )

  operation = AdGroupOperation(create=ad_group)
  try:
    response = service.mutate_ad_groups(
        customer_id=customer_id, operations=[operation]
    )
  except GoogleAdsException as e:
    _handle_google_ads_error(e)

  resource_name = response.results[0].resource_name
  return {"resource_name": resource_name}


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

  headline_assets = [AdTextAsset(text=h) for h in headlines]
  description_assets = [AdTextAsset(text=d) for d in descriptions]

  rsa_info = ResponsiveSearchAdInfo(
      headlines=headline_assets,
      descriptions=description_assets,
  )
  if path1:
    rsa_info.path1 = path1
  if path2:
    rsa_info.path2 = path2

  ad = Ad(
      final_urls=[final_url],
      responsive_search_ad=rsa_info,
  )

  ad_group_ad = AdGroupAd(
      ad_group=ad_group_resource_name,
      status=AdGroupAdStatusEnum.AdGroupAdStatus[status],
      ad=ad,
  )

  operation = AdGroupAdOperation(create=ad_group_ad)
  try:
    response = service.mutate_ad_group_ads(
        customer_id=customer_id, operations=[operation]
    )
  except GoogleAdsException as e:
    _handle_google_ads_error(e)

  resource_name = response.results[0].resource_name
  return {"resource_name": resource_name}


_MATCH_TYPE_MAP = {
    "EXACT": KeywordMatchTypeEnum.KeywordMatchType.EXACT,
    "PHRASE": KeywordMatchTypeEnum.KeywordMatchType.PHRASE,
    "BROAD": KeywordMatchTypeEnum.KeywordMatchType.BROAD,
}


@mcp.tool()
def create_keywords(
    customer_id: str,
    ad_group_resource_name: str,
    keywords: list[dict[str, str]],
    login_customer_id: str | None = None,
) -> dict[str, list[str]]:
  """Creates keywords in an ad group.

  Args:
      customer_id: Google Ads customer ID (digits only).
      ad_group_resource_name: Resource name from create_ad_group.
      keywords: List of keyword dicts, each with:
          - text: The keyword text (e.g., "ss john barry silver coin")
          - match_type: EXACT, PHRASE, or BROAD
      login_customer_id: MCC account ID if customer is managed.

  Returns:
      Dict with list of created keyword resource_names.
  """
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("AdGroupCriterionService")

  operations = []
  for kw in keywords:
    match_type = _MATCH_TYPE_MAP.get(kw["match_type"].upper())
    if not match_type:
      raise ToolError(
          f"Invalid match_type: {kw['match_type']}. "
          "Use EXACT, PHRASE, or BROAD."
      )

    criterion = AdGroupCriterion(
        ad_group=ad_group_resource_name,
        status=(
            AdGroupCriterionStatusEnum.AdGroupCriterionStatus.ENABLED
        ),
        keyword=KeywordInfo(text=kw["text"], match_type=match_type),
    )
    operations.append(AdGroupCriterionOperation(create=criterion))

  try:
    response = service.mutate_ad_group_criteria(
        customer_id=customer_id, operations=operations
    )
  except GoogleAdsException as e:
    _handle_google_ads_error(e)

  return {
      "resource_names": [r.resource_name for r in response.results]
  }


@mcp.tool()
def create_negative_campaign_keywords(
    customer_id: str,
    campaign_resource_name: str,
    keywords: list[str],
    login_customer_id: str | None = None,
) -> dict[str, list[str]]:
  """Creates negative keywords at the campaign level.

  Args:
      customer_id: Google Ads customer ID (digits only).
      campaign_resource_name: Resource name from create_search_campaign.
      keywords: List of negative keyword strings (e.g., ["free",
          "fake", "replica"]).
      login_customer_id: MCC account ID if customer is managed.

  Returns:
      Dict with list of created criterion resource_names.
  """
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("CampaignCriterionService")

  operations = []
  for kw_text in keywords:
    criterion = CampaignCriterion(
        campaign=campaign_resource_name,
        negative=True,
        keyword=KeywordInfo(
            text=kw_text,
            match_type=KeywordMatchTypeEnum.KeywordMatchType.BROAD,
        ),
    )
    operations.append(CampaignCriterionOperation(create=criterion))

  try:
    response = service.mutate_campaign_criteria(
        customer_id=customer_id, operations=operations
    )
  except GoogleAdsException as e:
    _handle_google_ads_error(e)

  return {
      "resource_names": [r.resource_name for r in response.results]
  }


@mcp.tool()
def create_geo_targeting(
    customer_id: str,
    campaign_resource_name: str,
    geo_target_constant_ids: list[int],
    login_customer_id: str | None = None,
) -> dict[str, list[str]]:
  """Adds location targeting to a campaign.

  Args:
      customer_id: Google Ads customer ID (digits only).
      campaign_resource_name: Resource name from create_search_campaign.
      geo_target_constant_ids: List of geo target constant IDs.
          Common values: 2840 (United States), 2124 (Canada).
      login_customer_id: MCC account ID if customer is managed.

  Returns:
      Dict with list of created criterion resource_names.
  """
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("CampaignCriterionService")
  geo_svc = ads_client.get_service("GeoTargetConstantService")

  operations = []
  for geo_id in geo_target_constant_ids:
    resource_name = geo_svc.geo_target_constant_path(geo_id)
    criterion = CampaignCriterion(
        campaign=campaign_resource_name,
        location=LocationInfo(
            geo_target_constant=resource_name,
        ),
    )
    operations.append(CampaignCriterionOperation(create=criterion))

  try:
    response = service.mutate_campaign_criteria(
        customer_id=customer_id, operations=operations
    )
  except GoogleAdsException as e:
    _handle_google_ads_error(e)

  return {
      "resource_names": [r.resource_name for r in response.results]
  }


@mcp.tool()
def remove_campaign_criterion(
    customer_id: str,
    campaign_id: str,
    criterion_id: str,
    login_customer_id: str | None = None,
) -> dict[str, str]:
  """Removes a campaign criterion (e.g., a geo target).

  Args:
      customer_id: Google Ads customer ID (digits only).
      campaign_id: Campaign ID (digits only).
      criterion_id: Criterion ID to remove (digits only).
      login_customer_id: MCC account ID if customer is managed.

  Returns:
      Dict with the removed resource_name.
  """
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("CampaignCriterionService")

  resource_name = service.campaign_criterion_path(
      customer_id, campaign_id, criterion_id
  )
  operation = CampaignCriterionOperation(remove=resource_name)

  try:
    response = service.mutate_campaign_criteria(
        customer_id=customer_id, operations=[operation]
    )
  except GoogleAdsException as e:
    _handle_google_ads_error(e)

  return {"removed": response.results[0].resource_name}


@mcp.tool()
def exclude_geo_targets(
    customer_id: str,
    campaign_resource_name: str,
    geo_target_constant_ids: list[int],
    login_customer_id: str | None = None,
) -> dict[str, list[str]]:
  """Excludes locations from a campaign (negative geo targeting).

  Args:
      customer_id: Google Ads customer ID (digits only).
      campaign_resource_name: Resource name from create_search_campaign.
      geo_target_constant_ids: List of geo target constant IDs to
          exclude.
      login_customer_id: MCC account ID if customer is managed.

  Returns:
      Dict with list of created exclusion resource_names.
  """
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("CampaignCriterionService")
  geo_svc = ads_client.get_service("GeoTargetConstantService")

  operations = []
  for geo_id in geo_target_constant_ids:
    resource_name = geo_svc.geo_target_constant_path(geo_id)
    criterion = CampaignCriterion(
        campaign=campaign_resource_name,
        negative=True,
        location=LocationInfo(
            geo_target_constant=resource_name,
        ),
    )
    operations.append(CampaignCriterionOperation(create=criterion))

  try:
    response = service.mutate_campaign_criteria(
        customer_id=customer_id, operations=operations
    )
  except GoogleAdsException as e:
    _handle_google_ads_error(e)

  return {
      "resource_names": [r.resource_name for r in response.results]
  }

@mcp.tool()
def remove_campaign_criterion(
    customer_id: str,
    campaign_id: str,
    criterion_id: str,
    login_customer_id: str | None = None,
) -> dict[str, str]:
  """Removes a campaign criterion (e.g., a geo target).

  Args:
      customer_id: Google Ads customer ID (digits only).
      campaign_id: Campaign ID (digits only).
      criterion_id: Criterion ID to remove (digits only).
      login_customer_id: MCC account ID if customer is managed.

  Returns:
      Dict with the removed resource_name.
  """
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("CampaignCriterionService")

  resource_name = service.campaign_criterion_path(
      customer_id, campaign_id, criterion_id
  )
  operation = CampaignCriterionOperation(remove=resource_name)

  try:
    response = service.mutate_campaign_criteria(
        customer_id=customer_id, operations=[operation]
    )
  except GoogleAdsException as e:
    _handle_google_ads_error(e)

  return {"removed": response.results[0].resource_name}


@mcp.tool()
def exclude_geo_targets(
    customer_id: str,
    campaign_resource_name: str,
    geo_target_constant_ids: list[int],
    login_customer_id: str | None = None,
) -> dict[str, list[str]]:
  """Excludes locations from a campaign (negative geo targeting).

  Args:
      customer_id: Google Ads customer ID (digits only).
      campaign_resource_name: Resource name from create_search_campaign.
      geo_target_constant_ids: List of geo target constant IDs to
          exclude.
      login_customer_id: MCC account ID if customer is managed.

  Returns:
      Dict with list of created exclusion resource_names.
  """
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("CampaignCriterionService")
  geo_svc = ads_client.get_service("GeoTargetConstantService")

  operations = []
  for geo_id in geo_target_constant_ids:
    resource_name = geo_svc.geo_target_constant_path(geo_id)
    criterion = CampaignCriterion(
        campaign=campaign_resource_name,
        negative=True,
        location=LocationInfo(
            geo_target_constant=resource_name,
        ),
    )
    operations.append(CampaignCriterionOperation(create=criterion))

  try:
    response = service.mutate_campaign_criteria(
        customer_id=customer_id, operations=operations
    )
  except GoogleAdsException as e:
    _handle_google_ads_error(e)

  return {
      "resource_names": [r.resource_name for r in response.results]
  }


@mcp.tool()
def update_campaign_status(
    customer_id: str,
    campaign_resource_name: str,
    status: str,
    login_customer_id: str | None = None,
) -> dict[str, str]:
  """Updates a campaign's status.

  Args:
      customer_id: Google Ads customer ID (digits only).
      campaign_resource_name: Full resource name of the campaign.
      status: New status: ENABLED or PAUSED.
      login_customer_id: MCC account ID if customer is managed.

  Returns:
      Dict with the updated campaign resource_name.
  """
  from google.protobuf import field_mask_pb2

  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("CampaignService")

  campaign = Campaign(
      resource_name=campaign_resource_name,
      status=CampaignStatusEnum.CampaignStatus[status],
  )

  operation = CampaignOperation(update=campaign)
  operation.update_mask.CopyFrom(
      field_mask_pb2.FieldMask(paths=["status"])
  )

  try:
    response = service.mutate_campaigns(
        customer_id=customer_id, operations=[operation]
    )
  except GoogleAdsException as e:
    _handle_google_ads_error(e)

  return {"resource_name": response.results[0].resource_name}