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

"""Reporting tools for Google Ads API."""

from google.protobuf import message
from google.protobuf.json_format import MessageToDict
import json
from typing import Any

from ads_mcp.coordinator import mcp_server as mcp
from ads_mcp.tools._utils import get_ads_client
from fastmcp.exceptions import ToolError
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.util import get_nested_attr
from google.ads.googleads.v24.services.services.google_ads_service import GoogleAdsServiceClient
import proto


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
    # convert to json first to avoid serialization issues
    return_value = proto.Message.to_dict(
        value,
        use_integers_for_enums=False,
    )
  elif isinstance(value, proto.Enum):
    return_value = value.name
  elif isinstance(value, message.Message):
    # Handle raw google.protobuf types that are not proto-plus messages.
    # (e.g. FieldMask from change_event.changed_fields)
    return_value = MessageToDict(value)
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
        Usually, it is the MCC on top of the target customer account. It is only
        digits. In most cases, a default account is set, it could be optional.

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
