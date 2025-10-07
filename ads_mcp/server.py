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

"""Google Ads MCP Server - Cloud Run compatible implementation."""

import asyncio
import sys
import os

def main():
    """Initialize and run the MCP server."""
    
    # Update views YAML if available
    try:
        from ads_mcp.scripts.generate_views import update_views_yaml
        asyncio.run(update_views_yaml())
        print("Views YAML updated successfully", file=sys.stderr)
    except Exception as e:
        print(f"Views YAML update skipped: {e}", file=sys.stderr)
    
    # Import tools to register them with MCP server
    import ads_mcp.tools.api  # This registers the @mcp_server.tool() functions
    import ads_mcp.tools.docs  # This registers documentation tools
    from ads_mcp.coordinator import mcp_server
    
    print("🚀 Google Ads MCP Server Started", file=sys.stderr)
    print("Available MCP tools:", file=sys.stderr)
    print("- list_accessible_accounts", file=sys.stderr)  
    print("- execute_gaql", file=sys.stderr)
    
    # Check if running in Cloud Run (has PORT environment variable)
    port = os.environ.get('PORT', 8080)
    if os.environ.get('PORT'):
        print(f"Running in Cloud Run mode on port {port}", file=sys.stderr)
        print("Starting FastMCP with streamable-http transport", file=sys.stderr)
        # Use FastMCP's native async HTTP transport (official Google Cloud approach)
        # This is the recommended way for Cloud Run deployment
        asyncio.run(
            mcp_server.run_async(
                transport="streamable-http",
                host="0.0.0.0",
                port=int(port)
            )
        )
    else:
        print("Running in local MCP mode", file=sys.stderr)
        # Run as pure MCP server for local development
        mcp_server.run()


if __name__ == "__main__":
    main()
