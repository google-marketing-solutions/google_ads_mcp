"""
Brand Configuration System
Manages brand-specific keywords, competitors, and targeting parameters
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum


class BrandCategory(Enum):
    """Product categories"""
    SKINCARE = "skincare"
    BEAUTY = "beauty"
    HAIRCARE = "haircare"
    WELLNESS = "wellness"


@dataclass
class BrandConfig:
    """Brand configuration for intelligence gathering"""
    brand_name: str
    parent_company: str
    category: BrandCategory

    # Search keywords for content discovery
    primary_keywords: List[str]
    secondary_keywords: List[str]
    product_keywords: List[str]

    # Competitive landscape
    direct_competitors: List[str]
    competitor_channels: List[str]

    # Target audience
    target_demographics: Dict[str, Any]

    # Content themes
    core_themes: List[str]

    # Analysis parameters
    analysis_config: Dict[str, Any]

    def get_all_keywords(self) -> List[str]:
        """Get all keywords for search"""
        return self.primary_keywords + self.secondary_keywords + self.product_keywords

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "brand_name": self.brand_name,
            "parent_company": self.parent_company,
            "category": self.category.value,
            "primary_keywords": self.primary_keywords,
            "secondary_keywords": self.secondary_keywords,
            "product_keywords": self.product_keywords,
            "direct_competitors": self.direct_competitors,
            "competitor_channels": self.competitor_channels,
            "target_demographics": self.target_demographics,
            "core_themes": self.core_themes,
            "analysis_config": self.analysis_config
        }


# Neutrogena Brand Configuration
NEUTROGENA_CONFIG = BrandConfig(
    brand_name="Neutrogena",
    parent_company="Kenvue",
    category=BrandCategory.SKINCARE,

    primary_keywords=[
        "Neutrogena",
        "Neutrogena skincare",
        "Neutrogena products",
        "Neutrogena review"
    ],

    secondary_keywords=[
        "dermatologist recommended skincare",
        "sensitive skin care",
        "acne treatment",
        "anti aging skincare",
        "hydrating face wash",
        "retinol serum",
        "sunscreen SPF",
        "cleansing face wash"
    ],

    product_keywords=[
        "Neutrogena Hydro Boost",
        "Neutrogena Rapid Wrinkle Repair",
        "Neutrogena Ultra Sheer Sunscreen",
        "Neutrogena Clear Pore",
        "Neutrogena Oil-Free Acne Wash",
        "Neutrogena Norwegian Formula",
        "Neutrogena Visibly Clear"
    ],

    direct_competitors=[
        "CeraVe",
        "La Roche-Posay",
        "Cetaphil",
        "Aveeno",
        "Eucerin"
    ],

    competitor_channels=[
        "UCcerave_official",  # Example channel IDs
        "UClaroche_posay",
        "UCcetaphil_official",
        "UCaveeno_official"
    ],

    target_demographics={
        "primary_age_range": "18-34",
        "secondary_age_range": "35-44",
        "gender_primary": "Female",
        "gender_secondary": "All",
        "interests": [
            "skincare",
            "beauty",
            "wellness",
            "self-care",
            "dermatology"
        ],
        "pain_points": [
            "acne",
            "aging concerns",
            "sensitive skin",
            "dryness",
            "sun protection"
        ]
    },

    core_themes=[
        "dermatologist recommended",
        "science-backed skincare",
        "sensitive skin solutions",
        "daily skincare routine",
        "acne solutions",
        "anti-aging innovation",
        "sun protection",
        "clean beauty"
    ],

    analysis_config={
        "videos_per_keyword": 25,
        "lookback_days": 30,
        "min_views_threshold": 1000,
        "min_engagement_rate": 2.0,
        "trend_velocity_threshold": 100,  # views per day
        "confidence_threshold": 0.80
    }
)


# Aveeno Brand Configuration (Kenvue portfolio)
AVEENO_CONFIG = BrandConfig(
    brand_name="Aveeno",
    parent_company="Kenvue",
    category=BrandCategory.SKINCARE,

    primary_keywords=[
        "Aveeno",
        "Aveeno skincare",
        "Aveeno products",
        "Aveeno daily moisturizer"
    ],

    secondary_keywords=[
        "oat skincare",
        "natural skincare",
        "eczema relief",
        "sensitive skin moisturizer",
        "gentle skincare",
        "soothing skincare"
    ],

    product_keywords=[
        "Aveeno Daily Moisturizing Lotion",
        "Aveeno Eczema Therapy",
        "Aveeno Calm + Restore",
        "Aveeno Positively Radiant",
        "Aveeno Skin Relief"
    ],

    direct_competitors=[
        "CeraVe",
        "Cetaphil",
        "Eucerin",
        "Vanicream"
    ],

    competitor_channels=[
        "UCcerave_official",
        "UCcetaphil_official",
        "UCeucerin_official"
    ],

    target_demographics={
        "primary_age_range": "25-44",
        "secondary_age_range": "45-60",
        "gender_primary": "Female",
        "gender_secondary": "All",
        "interests": [
            "natural skincare",
            "sensitive skin care",
            "eczema relief",
            "gentle beauty"
        ],
        "pain_points": [
            "eczema",
            "dry skin",
            "sensitive skin",
            "irritation",
            "natural ingredients preference"
        ]
    },

    core_themes=[
        "natural oat ingredients",
        "dermatologist recommended",
        "sensitive skin care",
        "eczema relief",
        "gentle effective",
        "daily moisture",
        "skin barrier repair"
    ],

    analysis_config={
        "videos_per_keyword": 25,
        "lookback_days": 30,
        "min_views_threshold": 1000,
        "min_engagement_rate": 2.0,
        "trend_velocity_threshold": 100,
        "confidence_threshold": 0.80
    }
)


# Listerine Brand Configuration (Kenvue portfolio)
LISTERINE_CONFIG = BrandConfig(
    brand_name="Listerine",
    parent_company="Kenvue",
    category=BrandCategory.WELLNESS,

    primary_keywords=[
        "Listerine",
        "Listerine mouthwash",
        "Listerine oral care"
    ],

    secondary_keywords=[
        "mouthwash routine",
        "oral hygiene",
        "fresh breath",
        "gum health",
        "teeth whitening mouthwash"
    ],

    product_keywords=[
        "Listerine Cool Mint",
        "Listerine Total Care",
        "Listerine Whitening",
        "Listerine Zero Alcohol"
    ],

    direct_competitors=[
        "Crest",
        "Colgate",
        "Scope",
        "ACT"
    ],

    competitor_channels=[
        "UCcrest_official",
        "UCcolgate_official"
    ],

    target_demographics={
        "primary_age_range": "18-44",
        "secondary_age_range": "45-60",
        "gender_primary": "All",
        "gender_secondary": "All",
        "interests": [
            "oral health",
            "wellness",
            "dental care",
            "fresh breath"
        ],
        "pain_points": [
            "bad breath",
            "gum health",
            "teeth staining",
            "plaque buildup"
        ]
    },

    core_themes=[
        "clinically proven",
        "total oral care",
        "gum health",
        "fresh breath confidence",
        "whitening",
        "oral hygiene routine"
    ],

    analysis_config={
        "videos_per_keyword": 20,
        "lookback_days": 30,
        "min_views_threshold": 1000,
        "min_engagement_rate": 2.0,
        "trend_velocity_threshold": 100,
        "confidence_threshold": 0.80
    }
)


# Brand Registry
BRAND_REGISTRY = {
    "neutrogena": NEUTROGENA_CONFIG,
    "aveeno": AVEENO_CONFIG,
    "listerine": LISTERINE_CONFIG
}


# Kenvue Portfolio Configuration
KENVUE_PORTFOLIO = {
    "company_name": "Kenvue",
    "brands": [
        "Neutrogena",
        "Aveeno",
        "Listerine",
        "Band-Aid",
        "Tylenol",
        "Johnson's Baby"
    ],
    "focus_categories": [
        BrandCategory.SKINCARE,
        BrandCategory.BEAUTY,
        BrandCategory.WELLNESS
    ],
    "portfolio_competitors": [
        "Unilever (Dove, Vaseline)",
        "L'Oréal (CeraVe, La Roche-Posay)",
        "Beiersdorf (Nivea, Eucerin)",
        "Procter & Gamble (Olay, Crest)"
    ]
}


def get_brand_config(brand_name: str) -> Optional[BrandConfig]:
    """
    Retrieve brand configuration by name

    Args:
        brand_name: Brand name (case-insensitive)

    Returns:
        BrandConfig if found, None otherwise
    """
    return BRAND_REGISTRY.get(brand_name.lower())


def list_available_brands() -> List[str]:
    """List all configured brands"""
    return list(BRAND_REGISTRY.keys())


def get_kenvue_brands() -> List[BrandConfig]:
    """Get all Kenvue brand configurations"""
    return [config for config in BRAND_REGISTRY.values()]


# Example usage
if __name__ == "__main__":
    # Demonstrate configuration access
    print("Available Brands:", list_available_brands())
    print()

    # Get Neutrogena config
    neutrogena = get_brand_config("neutrogena")
    if neutrogena:
        print(f"Brand: {neutrogena.brand_name}")
        print(f"Parent Company: {neutrogena.parent_company}")
        print(f"Category: {neutrogena.category.value}")
        print(f"Primary Keywords: {neutrogena.primary_keywords}")
        print(f"Direct Competitors: {neutrogena.direct_competitors}")
        print(f"Target Demo: {neutrogena.target_demographics['primary_age_range']}")
        print()

    # Show Kenvue portfolio
    print("Kenvue Portfolio Brands:")
    for brand_name in KENVUE_PORTFOLIO["brands"]:
        print(f"  - {brand_name}")
