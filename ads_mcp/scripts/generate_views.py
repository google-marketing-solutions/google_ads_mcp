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
"""Generates YAML files for Google Ads API reporting views."""

import asyncio
import logging
import os
from typing import Any, Literal

import httpx
import yaml

logging.getLogger("httpx").setLevel(logging.WARNING)

ADS_API_VERSION = "v22"
VIEW_JSON_URL_PATH = (
    f"https://gaql-query-builder.uc.r.appspot.com/schemas/{ADS_API_VERSION}/"
)
MODULE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTEXT_PATH = f"{MODULE_ROOT}/context"

http_client = httpx.AsyncClient(http2=True)


def get_view_json_url(view: str) -> str:
  return f"{VIEW_JSON_URL_PATH}{view}.json"


async def get_view_json(view: str) -> dict[str, Any]:
  """Fetches the JSON definition for a given reporting view."""
  http_res = await http_client.get(get_view_json_url(view))
  view_json = http_res.json()
  return view_json


# def get_view_json(view: str):
#     return json.load(open("ad_group_ad_asset_combination_view.json"))


def get_fields_obj(
    view_json: dict[str, Any],
    category: Literal["attributes", "segments", "metrics"],
) -> dict[str, Any]:
  """Extracts field metadata details for a given category from the view JSON."""
  selected_info = [
      "name",
      "description",
      "category",
      "data_type",
      "is_repeated",
      "enum_values",
      "filterable",
      "sortable",
  ]

  def detailed(field):
    return view_json["fields"][field]["field_details"]

  return {
      field: {i: detailed(field)[i] for i in selected_info}
      for field in view_json[category]
  }


async def save_view_yaml(view: str, path: str = "."):
  """Saves the reporting view metadata as a YAML file."""
  view_json = await get_view_json(view)

  attributed_views = set(
      v.split(".")[0]
      for v in view_json["attributes"]
      if not v.startswith(f"{view}.")
  )

  view_data = {
      "display_name": view_json["display_name"],
      "name": view_json["name"],
      "description": view_json["description"],
      "attributed_views": list(attributed_views),
      "attributes": get_fields_obj(view_json, "attributes"),
      "segments": get_fields_obj(view_json, "segments"),
      "metrics": get_fields_obj(view_json, "metrics"),
  }

  with open(os.path.join(path, f"{view}.yaml"), "w", encoding="utf-8") as f:
    yaml.safe_dump(view_data, f, sort_keys=False)


async def update_views_yaml():
  """Updates the YAML files for all reporting views."""
  if os.path.isfile(f"{CONTEXT_PATH}/.api-version"):
    with open(f"{CONTEXT_PATH}/.api-version", "r", encoding="utf-8") as f:
      if f.read().strip() == ADS_API_VERSION:
        return

  with open(f"{CONTEXT_PATH}/views.yaml", "r", encoding="utf-8") as f:
    views = yaml.safe_load(f)

  tasks = [save_view_yaml(view, f"{CONTEXT_PATH}/views") for view in views]
  await asyncio.gather(*tasks)

  with open(f"{CONTEXT_PATH}/.api-version", "w", encoding="utf-8") as f:
    f.write(ADS_API_VERSION)


if __name__ == "__main__":
  asyncio.run(update_views_yaml())
