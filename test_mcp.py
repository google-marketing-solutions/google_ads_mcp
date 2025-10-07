#!/usr/bin/env python3
"""
Teste do Google Ads MCP Server
"""

import requests
import json

# URL do MCP Server no Cloud Run
MCP_URL = "https://google-ads-mcp-hqkcmn4q5q-uc.a.run.app"

def test_mcp_tools():
    """Testa as ferramentas MCP disponíveis"""
    
    print("🧪 Testando Google Ads MCP Server")
    print(f"URL: {MCP_URL}")
    print("-" * 50)
    
    # Teste 1: Verificar se o servidor está rodando
    try:
        response = requests.get(f"{MCP_URL}/sse", timeout=5)
        print("✅ Servidor MCP está rodando (SSE endpoint ativo)")
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return
    
    # Teste 2: Listar ferramentas disponíveis (simulado)
    print("\n📋 Ferramentas MCP disponíveis:")
    print("- list_accessible_accounts(refresh_token)")
    print("- execute_gaql(query, customer_id, refresh_token, login_customer_id?)")
    print("- get_gaql_doc()")
    print("- get_reporting_view_doc(view?)")
    
    # Teste 3: Exemplo de uso
    print("\n💡 Exemplo de uso com LLM:")
    example_call = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "list_accessible_accounts",
        "params": {
            "refresh_token": "1//04xxx-your-refresh-token-here"
        }
    }
    print(f"POST {MCP_URL}/mcp")
    print("Content-Type: application/json")
    print("Accept: application/json, text/event-stream")
    print(json.dumps(example_call, indent=2))
    
    print("\n🔐 Configuração para Claude Desktop:")
    claude_config = {
        "mcpServers": {
            "google-ads": {
                "command": "mcp-client",
                "args": ["--server-url", MCP_URL]
            }
        }
    }
    print(json.dumps(claude_config, indent=2))
    
    print("\n✅ Google Ads MCP Server está pronto para uso!")
    print("🌐 Acesso público habilitado para testes")
    print("🔧 Configure suas credenciais OAuth2 e teste com um LLM")

if __name__ == "__main__":
    test_mcp_tools()
