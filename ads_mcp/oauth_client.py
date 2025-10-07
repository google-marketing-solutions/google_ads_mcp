#!/usr/bin/env python3
"""
Cliente OAuth dinâmico para Google Ads MCP
Busca tokens de acesso de uma API externa configurada via variáveis de ambiente
"""

import os
import requests
import logging
import time
from typing import Optional
from datetime import datetime
from flask import request

logger = logging.getLogger(__name__)

class DynamicOAuthClient:
    """Cliente para obter tokens OAuth dinamicamente de uma API externa"""
    
    def __init__(self):
        self.oauth_api_url = os.environ.get('OAUTH_API_URL')
        self.oauth_api_token = os.environ.get('OAUTH_API_TOKEN')
        self.google_ads_account_id = os.environ.get('GOOGLE_ADS_ACCOUNT_ID')
        self.token_cache = {}
        self._access_token = None
        self._token_expires_at = None
        
        logger.info(f"OAuth Client inicializado - URL: {self.oauth_api_url}, Account: {self.google_ads_account_id}")
        
    
    def _get_cache_key_for_refresh_token(self, refresh_token: str) -> str:
        """Gera chave de cache única baseada no refresh_token"""
        token_hash = abs(hash(refresh_token))
        return f"refresh_token_{token_hash}"
    
    def _generate_access_token_from_refresh(self, refresh_token: str) -> Optional[str]:
        """
        Gera access_token a partir do refresh_token usando credenciais da app
        Com cache individual por refresh_token para evitar renovações desnecessárias
        """
        # Verifica cache primeiro
        cache_key = self._get_cache_key_for_refresh_token(refresh_token)
        if cache_key in self.token_cache:
            cached_data = self.token_cache[cache_key]
            if cached_data['expires_at'] > time.time():
                logger.info(f"Usando access_token do cache para {refresh_token[:10]}...")
                return cached_data['access_token']
        
        try:
            # Lê credenciais do arquivo YAML (mais simples)
            import yaml
            from ads_mcp.utils import ROOT_DIR
            
            credentials_path = os.environ.get("GOOGLE_ADS_CREDENTIALS", f"{ROOT_DIR}/google-ads.yaml")
            
            if not os.path.isfile(credentials_path):
                logger.error(f"Arquivo de credenciais não encontrado: {credentials_path}")
                return None
                
            with open(credentials_path, "r", encoding="utf-8") as f:
                ads_config = yaml.safe_load(f.read())
                
            client_id = ads_config.get('client_id')
            client_secret = ads_config.get('client_secret')
            
            if not client_id or not client_secret:
                logger.error("client_id ou client_secret não encontrados no arquivo YAML")
                return None
            
            # Chama Google OAuth para refresh do token
            response = requests.post('https://oauth2.googleapis.com/token', {
                'client_id': client_id,
                'client_secret': client_secret,
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token'
            })
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get('access_token')
                expires_in = token_data.get('expires_in', 3600)  # Padrão: 1 hora
                
                if access_token:
                    # Armazena no cache com expiração
                    cache_key = self._get_cache_key_for_refresh_token(refresh_token)
                    self.token_cache[cache_key] = {
                        'access_token': access_token,
                        'expires_at': time.time() + expires_in - 60,  # 60s buffer
                        'refresh_token_hash': refresh_token[:10]  # Para debug
                    }
                    logger.info(f"Access token gerado e armazenado no cache para {refresh_token[:10]}...")
                    return access_token
                else:
                    logger.error("Access token não encontrado na resposta")
                    return None
            else:
                logger.error(f"Erro ao gerar access token: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao gerar access token: {e}")
            return None
    
    def _get_token_from_external_api(self) -> Optional[str]:
        """
        Obtém token da API externa (método original - fallback)
        """
        if not self.oauth_api_url or not self.google_ads_account_id:
            logger.warning("OAUTH_API_URL ou GOOGLE_ADS_ACCOUNT_ID não configurados")
            return None
            
        cache_key = f"google_ads_{self.google_ads_account_id}"
        
        # Verifica cache
        if cache_key in self.token_cache:
            cached_token = self.token_cache[cache_key]
            if cached_token['expires_at'] > datetime.utcnow():
                logger.debug("Usando token do cache")
                return cached_token['access_token']
                
        try:
            # Chama API externa para obter token
            headers = {
                'Content-Type': 'application/json'
            }
            
            if self.oauth_api_token:
                headers['Authorization'] = f'Bearer {self.oauth_api_token}'
                
            payload = {
                'account_id': self.google_ads_account_id,
                'scopes': ['https://www.googleapis.com/auth/adwords'],
                'service': 'google-ads'
            }
            
            logger.info(f"Solicitando token para conta {self.google_ads_account_id}")
            
            response = requests.post(
                f"{self.oauth_api_url}/oauth/google-ads/token",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get('access_token')
                expires_in = token_data.get('expires_in', 3600)
                
                if access_token:
                    self._access_token = access_token
                    self._token_expires_at = time.time() + expires_in - 60
                    logger.info(f"Token obtido com sucesso para conta {self.google_ads_account_id}")
                    return access_token
                else:
                    logger.error("Token não encontrado na resposta da API")
                    return None
            else:
                logger.error(f"Erro HTTP {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro de conexão com API OAuth: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado ao obter token: {e}")
            return None
            
    def get_access_token(self) -> Optional[str]:
        """
        Obtém access token válido, renovando se necessário
        
        Returns:
            Access token válido ou None se não disponível
        """
        # Primeiro, verifica se há token nos headers da requisição (dinâmico)
        if request and hasattr(request, 'headers'):
            header_token = request.headers.get('X-OAuth-Access-Token')
            if header_token:
                logger.info("Usando access token do header da requisição")
                return header_token
            
            # Se não tem access token, mas tem refresh token no header, renova
            header_refresh = request.headers.get('X-OAuth-Refresh-Token')
            if header_refresh:
                try:
                    logger.info("Renovando access token usando refresh token do header")
                    new_token = self._generate_access_token_from_refresh(header_refresh)
                    if new_token:
                        logger.info("Access token renovado com sucesso (header)")
                        return new_token
                except Exception as e:
                    logger.error(f"Erro ao renovar token do header: {e}")
        
        # Fallback: verifica se já tem token válido em cache
        if self._access_token and self._token_expires_at:
            if time.time() < self._token_expires_at - 60:  # 60s buffer
                logger.info("Usando access token em cache")
                return self._access_token
        
        # Sem refresh token local disponível
        logger.warning("Nenhum método de autenticação disponível")
        return None
            
    def clear_cache_for_refresh_token(self, refresh_token: str) -> None:
        """
        Limpa cache específico para um refresh_token
        """
        cache_key = self._get_cache_key_for_refresh_token(refresh_token)
        if cache_key in self.token_cache:
            del self.token_cache[cache_key]
            logger.info(f"Cache limpo para refresh_token {refresh_token[:10]}...")
    
    def refresh_token_if_needed(self) -> bool:
        """
        Força atualização do token se necessário
        Returns:
            True se token foi atualizado com sucesso
        """
        # Limpa cache para forçar nova requisição
        cache_key = f"google_ads_{self.google_ads_account_id}"
        if cache_key in self.token_cache:
            del self.token_cache[cache_key]
            
        token = self.get_access_token()
        return token is not None
    
    def get_cache_stats(self) -> dict:
        """
        Retorna estatísticas do cache para debug
        """
        stats = {
            'total_cached_tokens': len(self.token_cache),
            'cached_refresh_tokens': [],
            'expired_tokens': 0
        }
        
        current_time = time.time()
        for key, data in self.token_cache.items():
            if key.startswith('refresh_token_'):
                is_expired = data['expires_at'] <= current_time
                stats['cached_refresh_tokens'].append({
                    'hash': data.get('refresh_token_hash', 'unknown'),
                    'expires_in': max(0, int(data['expires_at'] - current_time)),
                    'expired': is_expired
                })
                if is_expired:
                    stats['expired_tokens'] += 1
        
        return stats
    
    def get_customer_id(self) -> Optional[str]:
        """
        Obtém customer_id dos headers da requisição ou variável de ambiente
        
        Returns:
            Customer ID ou None se não disponível
        """
        # Verifica header da requisição primeiro
        if request and hasattr(request, 'headers'):
            customer_id = request.headers.get('X-Google-Ads-Customer-ID')
            if customer_id:
                logger.info(f"Usando customer_id do header: {customer_id}")
                return customer_id
        
        # Fallback para variável de ambiente
        customer_id = os.environ.get('GOOGLE_ADS_CUSTOMER_ID')
        if customer_id:
            logger.info(f"Usando customer_id da variável de ambiente: {customer_id}")
            return customer_id
            
        logger.warning("Customer ID não encontrado nos headers nem variáveis de ambiente")
        return None

# Instância global
oauth_client = DynamicOAuthClient()
