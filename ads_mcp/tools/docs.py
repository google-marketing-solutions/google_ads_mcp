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

"""This module provides tools for accessing Google Ads API documentation."""

import os

import yaml

from ads_mcp.coordinator import mcp_server as mcp
from fastmcp.exceptions import ToolError
from ads_mcp.utils import MODULE_DIR


def _get_gaql_doc_content() -> str:
  """Reads the GAQL documentation."""
  with open(
      os.path.join(MODULE_DIR, "context/GAQL.md"), "r", encoding="utf-8"
  ) as f:
    data = f.read()
  return data


def _get_reporting_doc_content() -> str:
  """Reads the general reporting documentation."""
  with open(
      os.path.join(MODULE_DIR, "context/Google_Ads_API_Reporting_Views.md"),
      "r",
      encoding="utf-8",
  ) as f:
    data = f.read()
  return data


def _get_view_doc_content(view: str) -> str:
  """Reads documentation for a specific view."""
  expected_dir = os.path.realpath(os.path.join(MODULE_DIR, "context", "views"))
  target_file = os.path.join(expected_dir, f"{view}.yaml")
  resolved_path = os.path.realpath(target_file)

  if not resolved_path.startswith(expected_dir):
    return "Invalid view name."
  try:
    with open(
        target_file,
        "r",
        encoding="utf-8",
    ) as f:
      data = f.read()
  except FileNotFoundError:
    raise ToolError(f"No view resource with the name {view} was found.")
  return data


@mcp.tool()
def get_gaql_doc() -> str:
  """Get Google Ads Query Language (GAQL) guide docs in Markdown format."""
  return _get_gaql_doc_content()


@mcp.resource("resource://Google_Ads_Query_Language")
def get_gaql_doc_resource() -> str:
  """Get Google Ads Query Language (GAQL) guides."""
  return _get_gaql_doc_content()


@mcp.tool()
def get_reporting_view_doc(view: str | None = None) -> str:
  """Get Google Ads API reporting view docs.

  If a Google Ads API view resource is specific, the doc will include
  metadata and related fields for the view.
  If a view is not specified, a doc briefs all views will be returned.
  All docs are in YAML format.

  Args:
      view: (Optional) The name of the view resource. If not set, a doc briefs
      all views will be returned.
  """
  if view:
    return _get_view_doc_content(view)
  return _get_reporting_doc_content()


@mcp.resource("resource://Google_Ads_API_Reporting_Views")
def get_reporting_doc() -> str:
  """Get Google Ads API reporting view docs."""
  return _get_reporting_doc_content()


@mcp.resource("resource://views/{view}")
def get_view_doc(view: str) -> str:
  """Get resource view docs for a given Google Ads API view resource.

  Include fields metadata for each the view.

  Args:
      view: The name of the view resource.
  """
  return _get_view_doc_content(view)


__CACHED_FIELDS: dict = {}


@mcp.tool()
def get_reporting_fields_doc(fields: list[str]) -> str:
  """Get Google Ads API reporting query fields detailed docs.

  For each a Google Ads API view fields is specific, the detailed docs of the fields
  metadata will be return. Includes
  All docs are in YAML format.

  Args:
      fields: A list of field names.
  """
  global __CACHED_FIELDS
  if not len(__CACHED_FIELDS):
    with open(
        os.path.join(MODULE_DIR, "context/fields.yaml"),
        "r",
        encoding="utf-8",
    ) as f:
      __CACHED_FIELDS = yaml.safe_load(f)

  fields_info = {field: __CACHED_FIELDS.get(field) for field in fields}
  missing_fields = [field for field in fields if not fields_info[field]]
  if missing_fields:
    raise ToolError("Unknown fields: " + ", ".join(missing_fields))

  return yaml.dump(fields_info)
