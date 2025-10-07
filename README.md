# Google Ads MCP Server

A pure MCP (Model Context Protocol) server for Google Ads API integration, designed for direct LLM interaction.

## 🚀 Features

- **Pure MCP Implementation**: Direct integration with LLMs via MCP protocol
- **Google Ads API Integration**: Full access to Google Ads reporting and management
- **OAuth2 Authentication**: Secure authentication using FastMCP framework
- **Cloud Run Ready**: Containerized for easy deployment on Google Cloud Run
- **Production Ready**: Optimized for scalability and reliability

## 🛠️ Available MCP Tools

### `list_accessible_accounts`
Lists all Google Ads customer accounts accessible to the authenticated user.

**Parameters**:
- `refresh_token`: OAuth2 refresh token for the specific user/client

**Returns**: Array of customer IDs that can be used as `login_customer_id`

### `execute_gaql`
Executes Google Ads Query Language (GAQL) queries for reporting data.

**Parameters**:
- `query`: GAQL query string
- `customer_id`: Target customer account ID (digits only)
- `refresh_token`: OAuth2 refresh token for the specific user/client
- `login_customer_id`: Optional MCC account ID for authentication

**Returns**: Array of query result objects

## 🔐 Multi-Client Architecture

This MCP server supports multiple clients simultaneously, each with their own Google Ads credentials:

### Client Authentication Flow
1. **OAuth Setup**: Each client performs Google OAuth flow once to get `refresh_token`
2. **MCP Calls**: Client passes `refresh_token` as parameter in every MCP tool call
3. **Token Generation**: Server generates `access_token` from client's `refresh_token`
4. **API Access**: Server uses client-specific `access_token` to access Google Ads API

### Example Usage
```python
# Client A calls
mcp_client.call_tool("list_accessible_accounts", {
    "refresh_token": "1//04xxx-client-A-refresh-token"
})

# Client B calls  
mcp_client.call_tool("execute_gaql", {
    "query": "SELECT campaign.name FROM campaign",
    "customer_id": "1234567890", 
    "refresh_token": "1//04xxx-client-B-refresh-token"
})
```

### Security & Isolation
- ✅ **Complete Isolation**: Each client uses their own credentials
- ✅ **Separate Caching**: Tokens are cached separately per client
- ✅ **No Permanent Storage**: Refresh tokens are never stored permanently
- ✅ **Scalable**: Supports thousands of concurrent clients

## 🔧 Setup & Configuration

### 1. Prerequisites
- Google Ads API Developer Token
- OAuth2 Client Credentials (Google Cloud Console)
- Google Cloud Project (for Cloud Run deployment)

### 2. Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Configure credentials
cp google-ads.yaml.example google-ads.yaml
# Edit google-ads.yaml with your credentials

# Run the MCP server
python -m ads_mcp.server
```

### 3. Cloud Run Deployment
```bash
# Set your Google Cloud project
export GOOGLE_CLOUD_PROJECT="your-project-id"

# Deploy to Cloud Run
./deploy.sh
```

## 🔐 Authentication

The MCP server uses OAuth2 authentication through the FastMCP framework. Configure your credentials in `google-ads.yaml`:

```yaml
developer_token: "YOUR_DEVELOPER_TOKEN"
client_id: "YOUR_CLIENT_ID.apps.googleusercontent.com"
client_secret: "YOUR_CLIENT_SECRET"
refresh_token: "YOUR_REFRESH_TOKEN"
```

## 📊 Example GAQL Queries

### Campaign Performance
```sql
SELECT 
  campaign.id,
  campaign.name,
  campaign.status,
  metrics.impressions,
  metrics.clicks,
  metrics.ctr,
  metrics.cost_micros
FROM campaign
WHERE campaign.status = 'ENABLED'
```

### Keyword Performance
```sql
SELECT 
  ad_group_criterion.keyword.text,
  ad_group_criterion.keyword.match_type,
  metrics.impressions,
  metrics.clicks,
  metrics.cost_micros
FROM keyword_view
WHERE campaign.id = 'YOUR_CAMPAIGN_ID'
```

## 🌐 LLM Integration

This MCP server can be integrated with any LLM that supports the MCP protocol:

- **Claude Desktop**: Add server configuration to MCP settings
- **Custom LLM Applications**: Use MCP client libraries
- **API Integration**: Direct MCP protocol communication

## 🔍 Monitoring & Logging

- Health check endpoint: `/health`
- Structured logging to stdout/stderr
- Google Cloud Run metrics and monitoring
- Error handling with detailed error messages

## 📈 Scaling

The server is designed for production use:
- Stateless architecture
- Efficient connection pooling
- Automatic scaling on Cloud Run
- Resource optimization for cost efficiency

## 🛡️ Security

- OAuth2 secure authentication
- No hardcoded credentials
- Container security best practices
- Non-root user execution
- Input validation and sanitization

## 📞 Support

For issues and questions:
1. Check the logs for detailed error messages
2. Verify your Google Ads API credentials
3. Ensure proper OAuth2 setup
4. Review Google Ads API quotas and limits
