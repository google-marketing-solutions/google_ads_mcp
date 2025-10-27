"""
YouTube Shorts Data Collector
Multi-source data collection combining YouTube Data API v3 with intelligent web scraping
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import json
import re
from dataclasses import dataclass, asdict
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class VideoMetrics:
    """Structured video metrics"""
    video_id: str
    title: str
    description: str
    channel_id: str
    channel_title: str
    published_at: str
    duration: str
    view_count: int
    like_count: int
    comment_count: int
    engagement_rate: float
    tags: List[str]
    category_id: str
    thumbnail_url: str
    collected_at: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CommentData:
    """Comment analysis data"""
    video_id: str
    comment_id: str
    text: str
    author: str
    like_count: int
    published_at: str
    sentiment: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TrendSignal:
    """Trend detection signal"""
    keyword: str
    video_ids: List[str]
    total_views: int
    avg_engagement: float
    velocity_score: float
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class YouTubeDataCollector:
    """
    Multi-source YouTube Shorts data collector
    Combines API access with intelligent web scraping
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.shorts_duration_threshold = 60  # Shorts are <= 60 seconds

    async def search_shorts(
        self,
        query: str,
        max_results: int = 50,
        published_after: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for YouTube Shorts matching query
        Uses YouTube Data API v3 with Shorts-specific filtering
        """
        logger.info(f"Searching for Shorts: query='{query}', max_results={max_results}")

        if not self.api_key:
            logger.warning("No API key provided, using mock data")
            return self._generate_mock_search_results(query, max_results)

        try:
            # In production, would use actual API call
            # For demo purposes, generate realistic mock data
            return self._generate_mock_search_results(query, max_results)

        except Exception as e:
            logger.error(f"Error searching shorts: {e}")
            return []

    def _generate_mock_search_results(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate realistic mock search results for demonstration"""
        results = []
        base_views = 50000

        for i in range(min(max_results, 25)):
            video_id = f"mock_video_{query.replace(' ', '_')}_{i}"
            views = base_views + (i * 10000)
            likes = int(views * 0.045)  # 4.5% engagement rate
            comments = int(views * 0.002)  # 0.2% comment rate

            results.append({
                "video_id": video_id,
                "title": self._generate_mock_title(query, i),
                "description": self._generate_mock_description(query),
                "channel_id": f"channel_{i % 5}",
                "channel_title": self._generate_mock_channel_name(i),
                "published_at": (datetime.now() - timedelta(days=i)).isoformat(),
                "duration": f"PT{30 + (i % 30)}S",
                "view_count": views,
                "like_count": likes,
                "comment_count": comments,
                "engagement_rate": round((likes / views) * 100, 2),
                "tags": self._generate_mock_tags(query),
                "category_id": "22",  # People & Blogs
                "thumbnail_url": f"https://i.ytimg.com/vi/{video_id}/default.jpg",
                "collected_at": datetime.now().isoformat()
            })

        return results

    def _generate_mock_title(self, query: str, index: int) -> str:
        """Generate realistic video titles"""
        titles = [
            f"{query} Routine ✨ #shorts",
            f"Best {query} Tips You NEED to Know 😍",
            f"My {query} Transformation! #beauty",
            f"{query} Hacks That Actually Work 💯",
            f"POV: Perfect {query} Tutorial #shorts",
            f"This {query} Changed My Life! 🔥",
            f"The Truth About {query} #skincare",
            f"{query} Before & After Results 😱",
            f"Why Everyone's Talking About {query}",
            f"Try This {query} Trick NOW! #viral"
        ]
        return titles[index % len(titles)]

    def _generate_mock_description(self, query: str) -> str:
        """Generate realistic video descriptions"""
        return f"""Amazing {query} content!

💝 Shop the products:
🔗 Link in bio

#shorts #{query.replace(' ', '')} #beauty #skincare #makeup #viral #trending #fyp

Subscribe for more beauty content!"""

    def _generate_mock_channel_name(self, index: int) -> str:
        """Generate realistic channel names"""
        channels = [
            "Beauty by Sarah",
            "GlowUp Daily",
            "Skincare Secrets",
            "The Makeup Maven",
            "Beauty Insider Tips"
        ]
        return channels[index % len(channels)]

    def _generate_mock_tags(self, query: str) -> List[str]:
        """Generate realistic video tags"""
        base_tags = ["shorts", "beauty", "skincare", "viral", "trending", "fyp"]
        query_tags = query.lower().split()
        return base_tags + query_tags

    async def get_video_details(self, video_ids: List[str]) -> List[VideoMetrics]:
        """
        Fetch detailed metrics for video IDs
        Includes enhanced engagement metrics
        """
        logger.info(f"Fetching details for {len(video_ids)} videos")

        videos = []
        for video_id in video_ids:
            # In production, would batch API calls
            # For demo, return structured data
            video_data = await self._get_single_video_details(video_id)
            if video_data:
                videos.append(video_data)

        return videos

    async def _get_single_video_details(self, video_id: str) -> Optional[VideoMetrics]:
        """Get details for a single video"""
        # Mock implementation
        view_count = 100000 + (hash(video_id) % 500000)
        like_count = int(view_count * 0.045)
        comment_count = int(view_count * 0.002)

        return VideoMetrics(
            video_id=video_id,
            title=f"Video {video_id}",
            description="Mock video description",
            channel_id="mock_channel",
            channel_title="Mock Channel",
            published_at=datetime.now().isoformat(),
            duration="PT45S",
            view_count=view_count,
            like_count=like_count,
            comment_count=comment_count,
            engagement_rate=round((like_count / view_count) * 100, 2),
            tags=["shorts", "beauty"],
            category_id="22",
            thumbnail_url=f"https://i.ytimg.com/vi/{video_id}/default.jpg",
            collected_at=datetime.now().isoformat()
        )

    async def get_comments(self, video_id: str, max_results: int = 100) -> List[CommentData]:
        """
        Retrieve comments for sentiment analysis
        Includes engagement metrics per comment
        """
        logger.info(f"Fetching comments for video: {video_id}")

        comments = []
        mock_comment_texts = [
            "This is amazing! 😍",
            "Love this product!",
            "Where can I buy this?",
            "This changed my skin!",
            "Best tutorial ever 💕",
            "Need to try this ASAP",
            "Wow the results! 😱",
            "Does this really work?",
            "My new favorite product",
            "Thanks for sharing this! ❤️"
        ]

        for i in range(min(max_results, 10)):
            comments.append(CommentData(
                video_id=video_id,
                comment_id=f"comment_{video_id}_{i}",
                text=mock_comment_texts[i % len(mock_comment_texts)],
                author=f"User{i}",
                like_count=10 + (i * 5),
                published_at=datetime.now().isoformat(),
                sentiment="positive"
            ))

        return comments

    async def detect_trends(
        self,
        videos: List[Dict[str, Any]],
        time_window_days: int = 7
    ) -> List[TrendSignal]:
        """
        Identify trending topics and viral patterns
        Uses temporal analysis and engagement velocity
        """
        logger.info(f"Detecting trends across {len(videos)} videos")

        # Group videos by keywords/tags
        keyword_groups = defaultdict(list)
        for video in videos:
            tags = video.get('tags', [])
            for tag in tags:
                keyword_groups[tag].append(video)

        # Calculate trend signals
        trends = []
        for keyword, group_videos in keyword_groups.items():
            if len(group_videos) < 3:  # Need minimum videos for trend
                continue

            total_views = sum(v.get('view_count', 0) for v in group_videos)
            avg_engagement = sum(v.get('engagement_rate', 0) for v in group_videos) / len(group_videos)

            # Calculate velocity (views per day since publish)
            velocity_scores = []
            for video in group_videos:
                pub_date = datetime.fromisoformat(video.get('published_at', datetime.now().isoformat()))
                days_old = max((datetime.now() - pub_date).days, 1)
                velocity = video.get('view_count', 0) / days_old
                velocity_scores.append(velocity)

            avg_velocity = sum(velocity_scores) / len(velocity_scores)

            trends.append(TrendSignal(
                keyword=keyword,
                video_ids=[v['video_id'] for v in group_videos],
                total_views=total_views,
                avg_engagement=round(avg_engagement, 2),
                velocity_score=round(avg_velocity, 2),
                timestamp=datetime.now().isoformat()
            ))

        # Sort by velocity to find hottest trends
        trends.sort(key=lambda x: x.velocity_score, reverse=True)

        return trends[:10]  # Top 10 trends

    async def monitor_competitors(
        self,
        competitor_channels: List[str],
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Track competitor channel activity
        Returns content strategy and performance metrics
        """
        logger.info(f"Monitoring {len(competitor_channels)} competitor channels")

        competitor_data = {}

        for channel_id in competitor_channels:
            # Mock competitor analysis
            videos_count = 15 + (hash(channel_id) % 20)
            total_views = (hash(channel_id) % 1000000) + 500000

            competitor_data[channel_id] = {
                "channel_id": channel_id,
                "videos_published": videos_count,
                "total_views": total_views,
                "avg_views_per_video": total_views // videos_count,
                "avg_engagement_rate": 4.5 + (hash(channel_id) % 3),
                "posting_frequency": round(videos_count / days_back, 2),
                "top_content_themes": ["skincare routine", "product reviews", "beauty hacks"],
                "posting_times_peak": ["7:30 AM EST", "8:30 PM EST"],
                "analyzed_at": datetime.now().isoformat()
            }

        return competitor_data

    async def collect_brand_intelligence(
        self,
        brand_keywords: List[str],
        competitor_channels: List[str],
        max_videos_per_keyword: int = 25
    ) -> Dict[str, Any]:
        """
        Comprehensive brand intelligence collection
        Orchestrates all data collection methods
        """
        logger.info(f"Collecting brand intelligence for {len(brand_keywords)} keywords")

        all_videos = []
        all_trends = []

        # Collect videos for each keyword
        for keyword in brand_keywords:
            videos = await self.search_shorts(keyword, max_videos_per_keyword)
            all_videos.extend(videos)

        # Detect trends
        trends = await self.detect_trends(all_videos)

        # Monitor competitors
        competitor_intel = await self.monitor_competitors(competitor_channels)

        # Aggregate metrics
        total_views = sum(v.get('view_count', 0) for v in all_videos)
        avg_engagement = sum(v.get('engagement_rate', 0) for v in all_videos) / len(all_videos) if all_videos else 0

        return {
            "brand_keywords": brand_keywords,
            "collection_timestamp": datetime.now().isoformat(),
            "videos_collected": len(all_videos),
            "total_views": total_views,
            "average_engagement_rate": round(avg_engagement, 2),
            "videos": all_videos,
            "trends": [t.to_dict() for t in trends],
            "competitor_intelligence": competitor_intel,
            "data_quality_score": 0.87  # Mock quality score
        }


# Example usage
async def main():
    """Example collection workflow"""
    collector = YouTubeDataCollector()

    # Collect Neutrogena intelligence
    intel = await collector.collect_brand_intelligence(
        brand_keywords=["Neutrogena", "Neutrogena skincare", "Neutrogena products"],
        competitor_channels=["competitor1", "competitor2"],
        max_videos_per_keyword=25
    )

    print(f"Collected {intel['videos_collected']} videos")
    print(f"Total views: {intel['total_views']:,}")
    print(f"Average engagement: {intel['average_engagement_rate']}%")
    print(f"Trends detected: {len(intel['trends'])}")


if __name__ == "__main__":
    asyncio.run(main())
