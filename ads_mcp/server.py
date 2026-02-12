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

"""The server for the Google Ads API MCP."""
import asyncio
import os

from ads_mcp.coordinator import mcp_server
from ads_mcp.scripts.generate_views import update_views_yaml
from ads_mcp.tools import api
from ads_mcp.tools import docs
from ads_mcp.tools import mutations

import dotenv
from fastmcp.server.auth.providers.google import GoogleProvider
from fastmcp.server.auth.providers.google import GoogleTokenVerifier


dotenv.load_dotenv()


tools = [api, docs, mutations]

if os.getenv("USE_GOOGLE_OAUTH_ACCESS_TOKEN"):
  mcp_server.auth = GoogleTokenVerifier()

if os.getenv("FASTMCP_SERVER_AUTH_GOOGLE_CLIENT_ID") and os.getenv(
    "FASTMCP_SERVER_AUTH_GOOGLE_CLIENT_SECRET"
):
  base_url = os.getenv("FASTMCP_SERVER_BASE_URL", "http://localhost:8000")
  mcp_server.auth = GoogleProvider(
      base_url=base_url,
      required_scopes=["https://www.googleapis.com/auth/adwords"],
  )


def main():
  """Initializes and runs the MCP server."""
  asyncio.run(update_views_yaml())  # Check and update docs resource
  api.get_ads_client()  # Check Google Ads credentials
  print("mcp server starting...")
  mcp_server.run(
      transport="streamable-http",
      show_banner=False,
  )  # Initialize and run the server


if __name__ == "__main__":
  main()
