"""
YouTube Shorts Intelligence Platform

Enterprise-scale marketing intelligence system for YouTube Shorts analysis.

Main Components:
- data_collector: Multi-source data collection
- databricks_integration: Enterprise data warehousing
- agents: Five specialized AI agents
- config: Brand configuration system
"""

__version__ = "1.0.0"
__author__ = "Kenvue Data Engineering"

from .data_collector import YouTubeDataCollector
from .databricks_integration import DatabricksWarehouse
from .agents import (
    AgentOrchestrator,
    ContentDiscoveryAgent,
    ContextualIntelligenceAgent,
    AudienceInsightAgent,
    CreativeStrategyAgent,
    CompetitiveIntelligenceAgent
)
from .config import get_brand_config, list_available_brands

__all__ = [
    'YouTubeDataCollector',
    'DatabricksWarehouse',
    'AgentOrchestrator',
    'ContentDiscoveryAgent',
    'ContextualIntelligenceAgent',
    'AudienceInsightAgent',
    'CreativeStrategyAgent',
    'CompetitiveIntelligenceAgent',
    'get_brand_config',
    'list_available_brands'
]
