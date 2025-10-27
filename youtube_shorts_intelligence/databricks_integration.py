"""
Databricks Unity Catalog Integration
Enterprise data warehouse with medallion architecture (Bronze/Silver/Gold)
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import json
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataLayer(Enum):
    """Medallion architecture layers"""
    BRONZE = "bronze"  # Raw data
    SILVER = "silver"  # Cleaned and validated
    GOLD = "gold"      # Business-level aggregates


@dataclass
class TableSchema:
    """Unity Catalog table schema definition"""
    catalog: str
    schema: str
    table: str
    layer: DataLayer

    @property
    def full_name(self) -> str:
        return f"{self.catalog}.{self.schema}.{self.table}"


class DatabricksWarehouse:
    """
    Databricks Unity Catalog integration
    Implements medallion architecture for YouTube Shorts intelligence
    """

    def __init__(
        self,
        workspace_url: Optional[str] = None,
        access_token: Optional[str] = None,
        catalog: str = "youtube_intelligence"
    ):
        self.workspace_url = workspace_url
        self.access_token = access_token
        self.catalog = catalog
        self.connected = False

        # Define schemas for each layer
        self.schemas = {
            DataLayer.BRONZE: TableSchema(catalog, "raw_data", "shorts_raw", DataLayer.BRONZE),
            DataLayer.SILVER: TableSchema(catalog, "processed_data", "shorts_processed", DataLayer.SILVER),
            DataLayer.GOLD: TableSchema(catalog, "analytics", "brand_intelligence", DataLayer.GOLD)
        }

    async def connect(self) -> bool:
        """Establish connection to Databricks workspace"""
        logger.info(f"Connecting to Databricks workspace: {self.workspace_url}")

        if not self.workspace_url or not self.access_token:
            logger.warning("No credentials provided, using mock mode")
            self.connected = True
            return True

        try:
            # In production, would authenticate with Databricks
            self.connected = True
            logger.info("Connected to Databricks successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Databricks: {e}")
            return False

    async def create_schemas(self) -> bool:
        """Initialize Unity Catalog schemas for medallion architecture"""
        logger.info("Creating Unity Catalog schemas")

        try:
            # Create catalog
            await self._execute_sql(f"CREATE CATALOG IF NOT EXISTS {self.catalog}")

            # Create schemas for each layer
            await self._execute_sql(f"CREATE SCHEMA IF NOT EXISTS {self.catalog}.raw_data")
            await self._execute_sql(f"CREATE SCHEMA IF NOT EXISTS {self.catalog}.processed_data")
            await self._execute_sql(f"CREATE SCHEMA IF NOT EXISTS {self.catalog}.analytics")

            logger.info("Schemas created successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to create schemas: {e}")
            return False

    async def create_tables(self) -> bool:
        """Create Delta Lake tables for YouTube Shorts data"""
        logger.info("Creating Delta Lake tables")

        try:
            # Bronze layer: Raw video data
            await self._execute_sql(f"""
                CREATE TABLE IF NOT EXISTS {self.schemas[DataLayer.BRONZE].full_name} (
                    video_id STRING NOT NULL,
                    title STRING,
                    description STRING,
                    channel_id STRING,
                    channel_title STRING,
                    published_at TIMESTAMP,
                    duration STRING,
                    view_count BIGINT,
                    like_count BIGINT,
                    comment_count BIGINT,
                    engagement_rate DOUBLE,
                    tags ARRAY<STRING>,
                    category_id STRING,
                    thumbnail_url STRING,
                    collected_at TIMESTAMP,
                    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
                )
                USING DELTA
                PARTITIONED BY (DATE(collected_at))
                COMMENT 'Bronze layer: Raw YouTube Shorts data'
            """)

            # Silver layer: Processed and validated data
            await self._execute_sql(f"""
                CREATE TABLE IF NOT EXISTS {self.schemas[DataLayer.SILVER].full_name} (
                    video_id STRING NOT NULL,
                    title STRING,
                    channel_id STRING,
                    channel_title STRING,
                    published_date DATE,
                    view_count BIGINT,
                    like_count BIGINT,
                    comment_count BIGINT,
                    engagement_rate DOUBLE,
                    content_themes ARRAY<STRING>,
                    sentiment_score DOUBLE,
                    brand_mentions ARRAY<STRING>,
                    competitor_flag BOOLEAN,
                    quality_score DOUBLE,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
                )
                USING DELTA
                PARTITIONED BY (published_date)
                COMMENT 'Silver layer: Cleaned and validated YouTube Shorts data'
            """)

            # Gold layer: Business-level aggregates
            await self._execute_sql(f"""
                CREATE TABLE IF NOT EXISTS {self.schemas[DataLayer.GOLD].full_name} (
                    brand_name STRING,
                    analysis_date DATE,
                    total_videos INT,
                    total_views BIGINT,
                    avg_engagement_rate DOUBLE,
                    top_content_themes ARRAY<STRING>,
                    top_trending_topics ARRAY<STRING>,
                    competitor_share_of_voice DOUBLE,
                    sentiment_score DOUBLE,
                    strategic_recommendations ARRAY<STRING>,
                    confidence_score DOUBLE,
                    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
                )
                USING DELTA
                PARTITIONED BY (analysis_date)
                COMMENT 'Gold layer: Brand intelligence and strategic insights'
            """)

            logger.info("Tables created successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            return False

    async def ingest_bronze(self, videos: List[Dict[str, Any]]) -> bool:
        """
        Ingest raw video data into Bronze layer
        Preserves original structure with minimal transformation
        """
        logger.info(f"Ingesting {len(videos)} videos into Bronze layer")

        try:
            for video in videos:
                # Convert to DataFrame-compatible format
                record = self._prepare_bronze_record(video)

                # In production, would use Spark DataFrame append
                await self._insert_record(self.schemas[DataLayer.BRONZE], record)

            logger.info(f"Successfully ingested {len(videos)} videos into Bronze layer")
            return True

        except Exception as e:
            logger.error(f"Failed to ingest Bronze data: {e}")
            return False

    def _prepare_bronze_record(self, video: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare video data for Bronze layer insertion"""
        return {
            "video_id": video.get("video_id"),
            "title": video.get("title"),
            "description": video.get("description"),
            "channel_id": video.get("channel_id"),
            "channel_title": video.get("channel_title"),
            "published_at": video.get("published_at"),
            "duration": video.get("duration"),
            "view_count": video.get("view_count"),
            "like_count": video.get("like_count"),
            "comment_count": video.get("comment_count"),
            "engagement_rate": video.get("engagement_rate"),
            "tags": video.get("tags", []),
            "category_id": video.get("category_id"),
            "thumbnail_url": video.get("thumbnail_url"),
            "collected_at": video.get("collected_at"),
        }

    async def process_to_silver(self) -> bool:
        """
        Transform Bronze to Silver layer
        Applies data quality rules and enrichments
        """
        logger.info("Processing Bronze -> Silver transformation")

        try:
            # In production, would use Spark SQL with complex transformations
            transformation_sql = f"""
                INSERT INTO {self.schemas[DataLayer.SILVER].full_name}
                SELECT
                    video_id,
                    title,
                    channel_id,
                    channel_title,
                    DATE(published_at) as published_date,
                    view_count,
                    like_count,
                    comment_count,
                    engagement_rate,
                    tags as content_themes,
                    0.75 as sentiment_score,  -- Would be calculated
                    ARRAY() as brand_mentions,  -- Would be extracted
                    FALSE as competitor_flag,
                    0.85 as quality_score,  -- Would be calculated
                    CURRENT_TIMESTAMP() as processed_at
                FROM {self.schemas[DataLayer.BRONZE].full_name}
                WHERE DATE(collected_at) = CURRENT_DATE()
                AND view_count > 0  -- Quality filter
            """

            await self._execute_sql(transformation_sql)

            logger.info("Silver transformation completed successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to process Silver layer: {e}")
            return False

    async def aggregate_to_gold(self, brand_name: str) -> bool:
        """
        Create Gold layer business aggregates
        Generates strategic intelligence for brand
        """
        logger.info(f"Aggregating to Gold layer for brand: {brand_name}")

        try:
            aggregation_sql = f"""
                INSERT INTO {self.schemas[DataLayer.GOLD].full_name}
                SELECT
                    '{brand_name}' as brand_name,
                    CURRENT_DATE() as analysis_date,
                    COUNT(DISTINCT video_id) as total_videos,
                    SUM(view_count) as total_views,
                    AVG(engagement_rate) as avg_engagement_rate,
                    COLLECT_SET(content_themes) as top_content_themes,
                    ARRAY() as top_trending_topics,  -- Would be calculated
                    0.0 as competitor_share_of_voice,  -- Would be calculated
                    AVG(sentiment_score) as sentiment_score,
                    ARRAY() as strategic_recommendations,  -- Would be generated by agents
                    0.88 as confidence_score,
                    CURRENT_TIMESTAMP() as analyzed_at
                FROM {self.schemas[DataLayer.SILVER].full_name}
                WHERE published_date >= DATE_SUB(CURRENT_DATE(), 30)
                GROUP BY 1, 2
            """

            await self._execute_sql(aggregation_sql)

            logger.info("Gold aggregation completed successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to aggregate Gold layer: {e}")
            return False

    async def query_gold_layer(self, brand_name: str) -> Optional[Dict[str, Any]]:
        """Query Gold layer for brand intelligence"""
        logger.info(f"Querying Gold layer for brand: {brand_name}")

        try:
            query = f"""
                SELECT *
                FROM {self.schemas[DataLayer.GOLD].full_name}
                WHERE brand_name = '{brand_name}'
                ORDER BY analysis_date DESC
                LIMIT 1
            """

            result = await self._execute_query(query)

            if result:
                logger.info("Gold layer query successful")
                return result[0] if result else None
            else:
                return None

        except Exception as e:
            logger.error(f"Failed to query Gold layer: {e}")
            return None

    async def _execute_sql(self, sql: str) -> bool:
        """Execute SQL statement (mock implementation)"""
        logger.debug(f"Executing SQL: {sql[:100]}...")
        # In production, would use Databricks SQL API
        return True

    async def _insert_record(self, schema: TableSchema, record: Dict[str, Any]) -> bool:
        """Insert single record (mock implementation)"""
        logger.debug(f"Inserting record into {schema.full_name}")
        # In production, would use Databricks Delta Lake API
        return True

    async def _execute_query(self, sql: str) -> Optional[List[Dict[str, Any]]]:
        """Execute query and return results (mock implementation)"""
        logger.debug(f"Executing query: {sql[:100]}...")
        # Return mock result for demonstration
        return [{
            "brand_name": "Neutrogena",
            "analysis_date": datetime.now().date().isoformat(),
            "total_videos": 25,
            "total_views": 5500000,
            "avg_engagement_rate": 4.73,
            "top_content_themes": ["skincare routine", "product reviews", "beauty hacks"],
            "confidence_score": 0.88
        }]

    async def run_full_pipeline(self, videos: List[Dict[str, Any]], brand_name: str) -> bool:
        """
        Execute complete ETL pipeline: Bronze -> Silver -> Gold
        """
        logger.info(f"Running full pipeline for {len(videos)} videos")

        try:
            # Ensure connection
            if not self.connected:
                await self.connect()

            # Create schemas and tables
            await self.create_schemas()
            await self.create_tables()

            # Bronze: Ingest raw data
            await self.ingest_bronze(videos)

            # Silver: Transform and enrich
            await self.process_to_silver()

            # Gold: Aggregate business metrics
            await self.aggregate_to_gold(brand_name)

            logger.info("Full pipeline completed successfully")
            return True

        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            return False


# Example usage
async def main():
    """Example warehouse workflow"""
    warehouse = DatabricksWarehouse(
        workspace_url="https://your-workspace.cloud.databricks.com",
        access_token="your-token",
        catalog="youtube_intelligence"
    )

    # Connect and initialize
    await warehouse.connect()
    await warehouse.create_schemas()
    await warehouse.create_tables()

    # Mock video data
    videos = [{
        "video_id": "test123",
        "title": "Test Video",
        "view_count": 100000,
        "engagement_rate": 4.5
    }]

    # Run pipeline
    await warehouse.run_full_pipeline(videos, "Neutrogena")

    # Query results
    results = await warehouse.query_gold_layer("Neutrogena")
    print(f"Gold layer results: {results}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
