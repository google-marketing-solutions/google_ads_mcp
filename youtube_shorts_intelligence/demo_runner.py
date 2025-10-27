"""
Production Demo Runner
Complete end-to-end demonstration of YouTube Shorts Intelligence Platform
"""

import asyncio
import logging
import os
import json
from datetime import datetime
from typing import Optional

from data_collector import YouTubeDataCollector
from databricks_integration import DatabricksWarehouse
from agents import AgentOrchestrator
from config import get_brand_config, list_available_brands

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class YouTubeShortsIntelligencePlatform:
    """
    Complete YouTube Shorts Intelligence Platform
    Orchestrates data collection, warehousing, and AI analysis
    """

    def __init__(
        self,
        youtube_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        databricks_url: Optional[str] = None,
        databricks_token: Optional[str] = None
    ):
        self.youtube_api_key = youtube_api_key
        self.anthropic_api_key = anthropic_api_key

        # Initialize components
        self.collector = YouTubeDataCollector(api_key=youtube_api_key)
        self.warehouse = DatabricksWarehouse(
            workspace_url=databricks_url,
            access_token=databricks_token
        )
        self.orchestrator = AgentOrchestrator(api_key=anthropic_api_key)

        logger.info("YouTube Shorts Intelligence Platform initialized")

    async def run_brand_intelligence(
        self,
        brand_name: str,
        output_dir: str = "./outputs"
    ) -> dict:
        """
        Execute complete intelligence pipeline for a brand

        Args:
            brand_name: Brand to analyze
            output_dir: Directory for output files

        Returns:
            Complete intelligence report
        """
        logger.info(f"=" * 80)
        logger.info(f"YOUTUBE SHORTS INTELLIGENCE PLATFORM")
        logger.info(f"Brand: {brand_name}")
        logger.info(f"Timestamp: {datetime.now().isoformat()}")
        logger.info(f"=" * 80)

        # Load brand configuration
        brand_config = get_brand_config(brand_name)
        if not brand_config:
            raise ValueError(f"Unknown brand: {brand_name}. Available: {list_available_brands()}")

        logger.info(f"Loaded configuration for {brand_config.brand_name}")
        logger.info(f"Parent Company: {brand_config.parent_company}")
        logger.info(f"Category: {brand_config.category.value}")

        # PHASE 1: Data Collection
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 1: DATA COLLECTION")
        logger.info("=" * 80)

        collection_data = await self._collect_data(brand_config)
        logger.info(f"✓ Collected {collection_data['videos_collected']} videos")
        logger.info(f"✓ Total views: {collection_data['total_views']:,}")
        logger.info(f"✓ Average engagement: {collection_data['average_engagement_rate']:.2f}%")

        # PHASE 2: Data Warehousing
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 2: DATA WAREHOUSING")
        logger.info("=" * 80)

        warehouse_success = await self._warehouse_data(collection_data, brand_config.brand_name)
        if warehouse_success:
            logger.info("✓ Data successfully ingested into Databricks")
            logger.info("✓ Bronze -> Silver -> Gold transformations complete")
        else:
            logger.warning("⚠ Warehouse ingestion completed with warnings")

        # PHASE 3: AI Agent Analysis
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 3: AI AGENT ANALYSIS")
        logger.info("=" * 80)

        intelligence_report = await self._analyze_data(collection_data)
        logger.info(f"✓ Analysis complete: {intelligence_report['synthesis']['total_insights_generated']} insights generated")
        logger.info(f"✓ Overall confidence: {intelligence_report['overall_confidence'] * 100:.0f}%")

        # PHASE 4: Output Generation
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 4: OUTPUT GENERATION")
        logger.info("=" * 80)

        outputs = await self._generate_outputs(
            collection_data,
            intelligence_report,
            brand_config,
            output_dir
        )

        logger.info(f"✓ Outputs saved to: {output_dir}")
        logger.info(f"  - Data: {outputs['data_file']}")
        logger.info(f"  - Report: {outputs['report_file']}")
        logger.info(f"  - Intelligence: {outputs['intelligence_file']}")

        # Display Executive Summary
        logger.info("\n" + "=" * 80)
        logger.info("EXECUTIVE SUMMARY")
        logger.info("=" * 80)
        print(intelligence_report['executive_summary'])

        logger.info("\n" + "=" * 80)
        logger.info("PIPELINE COMPLETE")
        logger.info("=" * 80)

        return {
            "brand_name": brand_config.brand_name,
            "collection_data": collection_data,
            "intelligence_report": intelligence_report,
            "outputs": outputs,
            "execution_timestamp": datetime.now().isoformat()
        }

    async def _collect_data(self, brand_config) -> dict:
        """Execute data collection phase"""
        logger.info("Initializing multi-source data collection...")

        # Collect brand intelligence
        intel = await self.collector.collect_brand_intelligence(
            brand_keywords=brand_config.primary_keywords[:3],  # Limit for demo
            competitor_channels=brand_config.competitor_channels,
            max_videos_per_keyword=brand_config.analysis_config['videos_per_keyword']
        )

        return intel

    async def _warehouse_data(self, collection_data: dict, brand_name: str) -> bool:
        """Execute data warehousing phase"""
        logger.info("Connecting to Databricks Unity Catalog...")

        try:
            # Connect
            await self.warehouse.connect()

            # Initialize schemas
            await self.warehouse.create_schemas()
            await self.warehouse.create_tables()

            # Run ETL pipeline
            videos = collection_data.get('videos', [])
            await self.warehouse.run_full_pipeline(videos, brand_name)

            return True

        except Exception as e:
            logger.error(f"Warehouse error: {e}")
            return False

    async def _analyze_data(self, collection_data: dict) -> dict:
        """Execute AI agent analysis phase"""
        logger.info("Launching AI agent orchestration...")
        logger.info("  → Content Discovery Agent")
        logger.info("  → Contextual Intelligence Agent")
        logger.info("  → Audience Insight Agent")
        logger.info("  → Creative Strategy Agent")
        logger.info("  → Competitive Intelligence Agent")

        # Run all agents
        intelligence = await self.orchestrator.run_full_analysis(collection_data)

        return intelligence

    async def _generate_outputs(
        self,
        collection_data: dict,
        intelligence_report: dict,
        brand_config,
        output_dir: str
    ) -> dict:
        """Generate output files"""
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save raw data
        data_file = os.path.join(
            output_dir,
            f"{brand_config.brand_name.lower()}_data_{timestamp}.json"
        )
        with open(data_file, 'w') as f:
            json.dump(collection_data, f, indent=2)

        # Save intelligence report
        intelligence_file = os.path.join(
            output_dir,
            f"{brand_config.brand_name.lower()}_intelligence_{timestamp}.json"
        )
        with open(intelligence_file, 'w') as f:
            json.dump(intelligence_report, f, indent=2)

        # Generate text report
        report_file = os.path.join(
            output_dir,
            f"{brand_config.brand_name.lower()}_report_{timestamp}.txt"
        )
        with open(report_file, 'w') as f:
            f.write(self._format_text_report(collection_data, intelligence_report, brand_config))

        return {
            "data_file": data_file,
            "intelligence_file": intelligence_file,
            "report_file": report_file
        }

    def _format_text_report(self, collection_data, intelligence_report, brand_config) -> str:
        """Format human-readable text report"""
        report = f"""
{'=' * 100}
YOUTUBE SHORTS INTELLIGENCE REPORT
{'=' * 100}

Brand: {brand_config.brand_name}
Parent Company: {brand_config.parent_company}
Category: {brand_config.category.value.upper()}
Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'=' * 100}
DATA COLLECTION SUMMARY
{'=' * 100}

Videos Analyzed: {collection_data['videos_collected']}
Total Views: {collection_data['total_views']:,}
Average Engagement Rate: {collection_data['average_engagement_rate']:.2f}%
Trends Detected: {len(collection_data.get('trends', []))}
Data Quality Score: {collection_data.get('data_quality_score', 0) * 100:.0f}%

{'=' * 100}
AI AGENT INSIGHTS
{'=' * 100}

Total Insights Generated: {intelligence_report['synthesis']['total_insights_generated']}
High Priority Actions: {intelligence_report['synthesis']['high_priority_actions']}
Overall Confidence: {intelligence_report['overall_confidence'] * 100:.0f}%

KEY THEMES:
"""
        for i, theme in enumerate(intelligence_report['synthesis']['key_themes'], 1):
            report += f"{i}. {theme}\n"

        report += f"""
IMMEDIATE ACTIONS:
"""
        for i, action in enumerate(intelligence_report['synthesis']['immediate_actions'], 1):
            report += f"{i}. {action}\n"

        report += f"""
{'=' * 100}
EXECUTIVE SUMMARY
{'=' * 100}
{intelligence_report['executive_summary']}

{'=' * 100}
END OF REPORT
{'=' * 100}
"""
        return report


async def main():
    """
    Main demo execution
    Run complete pipeline for Neutrogena
    """

    # Get API keys from environment
    youtube_api_key = os.getenv('YOUTUBE_API_KEY')
    anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
    databricks_url = os.getenv('DATABRICKS_WORKSPACE_URL')
    databricks_token = os.getenv('DATABRICKS_ACCESS_TOKEN')

    # Show configuration status
    print("\n" + "=" * 80)
    print("CONFIGURATION STATUS")
    print("=" * 80)
    print(f"YouTube API Key: {'✓ Configured' if youtube_api_key else '✗ Not configured (using mock data)'}")
    print(f"Anthropic API Key: {'✓ Configured' if anthropic_api_key else '✗ Not configured (using mock analysis)'}")
    print(f"Databricks Workspace: {'✓ Configured' if databricks_url else '✗ Not configured (using mock warehouse)'}")
    print("=" * 80 + "\n")

    # Initialize platform
    platform = YouTubeShortsIntelligencePlatform(
        youtube_api_key=youtube_api_key,
        anthropic_api_key=anthropic_api_key,
        databricks_url=databricks_url,
        databricks_token=databricks_token
    )

    # Run intelligence for Neutrogena
    results = await platform.run_brand_intelligence(
        brand_name="neutrogena",
        output_dir="./outputs"
    )

    print("\n✓ Demo complete! Check ./outputs directory for results.")


if __name__ == "__main__":
    asyncio.run(main())
