# Google Ads MCP Server

## Project Overview
The **Google Ads MCP Server** is a Python implementation of the Model Context Protocol (MCP) that bridges Large Language Models (LLMs), such as Gemini, with the Google Ads API. It allows users to interact with their Google Ads accounts using natural language queries to retrieve campaigns, metrics, and other data.

It exposes several MCP tools and resources:
*   **Tools:**
    *   `execute_gaql`: Execute Google Ads Query Language queries.
    *   `list_accessible_accounts`: List accessible customer IDs.
    *   `get_gaql_doc`: Retrieve GAQL grammar documentation.
    *   `get_reporting_view_doc`: Retrieve documentation for specific reporting views (e.g., campaign, ad_group).
*   **Resources:**
    *   `resource://Google_Ads_Query_Language`: GAQL guide.
    *   `resource://Google_Ads_API_Reporting_Views`: Overview of reporting views.
    *   `resource://views/{view}`: Detailed metadata for specific views.

## Tech Stack
*   **Language:** Python 3.12+
*   **Package Manager:** `uv`
*   **Key Libraries:**
    *   `fastmcp`: For building the MCP server.
    *   `google-ads`: Official Google Ads API client.
    *   `mcp`: Core MCP library.
    *   `pytest`: Testing framework.
*   **Tooling:**
    *   `pyink`: Auto-formatter (Google style).
    *   `pylint`: Linter.

## Project Structure
*   `ads_mcp/`: Main source code directory.
    *   `server.py`: Entry point for the MCP server.
    *   `coordinator.py`: Server coordinator logic.
    *   `tools/`: Specific MCP tools implementation.
        *   `api.py`: Tools for direct interaction with Google Ads API (e.g., executing GAQL).
        *   `docs.py`: Documentation tools exposing `context/` files.
    *   `context/`: Context resources.
        *   `GAQL.md`: GAQL grammar documentation.
        *   `views/`: YAML definitions for reporting views.
*   `tests/`: Test suite mirroring the source structure.
*   `pyproject.toml`: Project configuration and dependencies.
*   `LLM.md`: Specific instructions for LLM agents.

## Setup & Development

### Prerequisites
*   Python 3.12 or higher.
*   `uv` installed (`pip install uv` or via other methods).
*   **Credentials:** A `google-ads.yaml` file is required for authentication. This file should contain `client_id`, `client_secret`, `refresh_token`, and `developer_token`.

### Installation
Sync dependencies using `uv`:

```bash
uv pip sync
# OR just
uv sync
```

### Key Commands

**Run the Server:**
To start the MCP server locally:
```bash
uv run -m ads_mcp.server
```

**Run Tests:**
Execute the test suite using `pytest`:
```bash
uv run pytest
```

**Formatting:**
Format code using `pyink` (enforces Google Style):
```bash
uv run pyink .
```

**Linting:**
Check for errors using `pylint`:
```bash
uv run pylint ads_mcp tests
```

## Development Conventions
*   **Style Guide:** Follow the **Google Python Style Guide**.
    *   **Indentation:** 2 spaces (no tabs).
    *   **Line Length:** 79 characters.
    *   **Vertical Alignment:** Align wrapped elements vertically or use a hanging 4-space indent.
*   **Testing:**
    *   Write test cases using the Python built-in `unittest` module.
    *   Run tests using `pytest`.
    *   **MCP Tool Testing:** When testing functions decorated with `@mcp.tool()`, access the underlying function via the `.fn` attribute (e.g., `api.tool_name.fn()`).
    *   New features must include corresponding tests.
*   **Environment Variables:**
    *   `GOOGLE_ADS_CREDENTIALS`: Path to the `google-ads.yaml` file (defaults to `$ROOT_DIR/google-ads.yaml`).
    *   `USE_GOOGLE_OAUTH_ACCESS_TOKEN`: Set to enable Google OAuth token verification.
