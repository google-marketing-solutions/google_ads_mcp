# Google Ads MCP Server

The Google Ads MCP Server is an implementation of the Model Context Protocol (MCP) that enables Large Language Models (LLMs), such as Gemini, to interact directly with the Google Ads API.

**This is not an officially supported Google product.**

## Disclaimer

Copyright Google LLC. Supported by Google LLC and/or its affiliate(s). This solution, including any related sample code or data, is made available on an “as is,” “as available,” and “with all faults” basis, solely for illustrative purposes, and without warranty or representation of any kind. This solution is experimental, unsupported and provided solely for your convenience. Your use of it is subject to your agreements with Google, as applicable, and may constitute a beta feature as defined under those agreements. To the extent that you make any data available to Google in connection with your use of the solution, you represent and warrant that you have all necessary and appropriate rights, consents and permissions to permit Google to use and process that data. By using any portion of this solution, you acknowledge, assume and accept all risks, known and unknown, associated with its usage and any processing of data by Google, including with respect to your deployment of any portion of this solution in your systems, or usage in connection with your business, if at all. With respect to the entrustment of personal information to Google, you will verify that the established system is sufficient by checking Google's privacy policy and other public information, and you agree that no further information will be provided by Google.

## Getting Started

Follow these instructions to configure and run the Google Ads MCP Server.

### 1. Configure Python Environment

#### For Direct Use

This project needs Python 3.12 with `pipx` or `uv`.

#### For Development

This project uses [`uv`](https://github.com/astral-sh/uv) for dependency management.

Install `uv` and then run the following command to install the required Python packages:

```bash
uv pip sync
```

### 2. Configure Google Ads credentials

This tool requires you to have a `google-ads.yaml` file with your Google Ads API credentials. By default, the application will look for this file in your home directory.

If you don't have one, you can generate it by running the following example from the `google-ads-python` library:
[authentication example](https://github.com/googleads/google-ads-python/blob/main/examples/authentication/generate_user_credentials.py)

Make sure your `google-ads.yaml` file contains the following keys:

- `client_id`
- `client_secret`
- `refresh_token`
- `developer_token`
- `login_customer_id` (optional, but recommended)

### 3. Launch MCP Server

#### For Direct Use with Gemini CLI

Update your Gemini configuration to include the `google-ads-mcp` server. The following is an example of a local MCP server configuration:

```json5
{
  // Other configs...
  "mcpServers": {
    "GoogleAds": {
      "command": "pipx",
      "args": [
        "run",
        "--spec",
        "git+https://github.com/google-marketing-solutions/google_ads_mcp.git",
        "run-mcp-server"
      ],
      "env": {
        "GOOGLE_ADS_CREDENTIALS": "PATH_TO_YAML"
      },
      "timeout": 30000,
      "trust": false
    }
  }
}
```

Once the server is running, you can interact with it using the Gemini CLI. Type `/mcp` in Gemini to see the `Google Ads API` server listed in the results.

#### For Local Development with Gemini CLI

Update your Gemini configuration to include the `google-ads-mcp` server. `[DIRECTORY]` will be the absolute path to the project. The following is an example of a local MCP server configuration:

```json5
{
  // Other configs...
  "mcpServers": {
    "GoogleAds": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "[DIRECTORY]",
        "-m",
        "ads_mcp.server"
      ],
      "cwd": "[DIRECTORY]",
      "timeout": 30000,
      "trust": false
    }
  }
}
```

Once the server is running, you can interact with it using the Gemini CLI. Type `/mcp` in Gemini to see the `Google Ads API` server listed in the results.

You can then ask questions like:

- "list all campaigns"
- "show me metrics for campaign `[CAMPAIGN_ID]`"
- "get all ad groups"

#### For Other MCP Clients (stdio transport)

Some MCP clients require stdio transport instead of streamable-http. Set the `MCP_TRANSPORT` environment variable to `stdio`:

```json
{
  "mcpServers": {
    "google-ads": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/google-marketing-solutions/google_ads_mcp.git",
        "run-mcp-server"
      ],
      "env": {
        "MCP_TRANSPORT": "stdio",
        "GOOGLE_ADS_CREDENTIALS": "PATH_TO_YAML"
      }
    }
  }
}
```

#### Direct Launch

To start the server directly, in the project path, run the following command:

```bash
uv run -m ads_mcp.server
```

The server will start and be ready to accept requests.

You can specify the transport mode via the `MCP_TRANSPORT` environment variable:

| Transport | Use Case | Example |
|-----------|----------|---------|
| `streamable-http` | HTTP-based clients (default) | `uv run -m ads_mcp.server` |
| `stdio` | CLI-based MCP clients | `MCP_TRANSPORT=stdio uv run -m ads_mcp.server` |
| `sse` | Server-Sent Events | `MCP_TRANSPORT=sse uv run -m ads_mcp.server` |

## Contributing

We welcome contributions! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) guide for details.

## License

Google Ads MCP Server is an open-source project licensed under the [APACHE-2.0 License](LICENSE).

## Contact

If you have any questions, suggestions, or feedback, please feel free to open an issue.
