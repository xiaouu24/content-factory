from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Literal, Dict, Any
from datetime import datetime

class ContentBrief(BaseModel):
    product_name: str
    product_category: str = "multimodal_llm_api"
    target_segments: List[str] = ["individual_developers", "enterprise_developers", "creators"]
    audience: str
    objective: str
    angle: str
    key_points: List[str]
    keywords: List[str]
    persona: str
    tone: str
    outline: List[str]
    cta: str
    models_to_feature: List[str] = ["text-to-image", "text-to-video"]
    enterprise_features: List[str] = ["SLA", "SSO/SAML", "VPC peering", "Data privacy controls"]
    pricing_angles: List[str] = ["free credits", "usage-based", "prepaid options"]
    compliance: List[str] = ["SOC 2", "GDPR"]
    visual_theme: Optional[str] = "cinematic, clean UI overlays"
    canonical_url: Optional[HttpUrl] = None
    # Vector store metadata
    generated_at: Optional[datetime] = Field(default_factory=datetime.now)
    vector_id: Optional[str] = None
    similarity_score: Optional[float] = None

class BlogArticle(BaseModel):
    title: str
    slug: str
    meta_description: str
    word_count_target: int = Field(default=1500)
    body_markdown: str
    # Analytics metadata
    actual_word_count: Optional[int] = None
    readability_score: Optional[float] = None
    vector_id: Optional[str] = None
    performance_metrics: Optional[Dict[str, Any]] = None

class SocialPost(BaseModel):
    platform: Literal["x", "linkedin"]
    persona: Literal["developer", "creator"] = "developer"
    variants: List[str]
    suggested_hashtags: List[str]
    link_handling: str   # e.g., "add UTM", "link-in-comments"
    asset_refs: List[str] = []  # IDs or URLs for images to attach
    # Performance tracking
    variant_ids: Optional[List[str]] = None  # Vector store IDs for each variant
    engagement_predictions: Optional[Dict[str, float]] = None

class ImageAsset(BaseModel):
    usage: Literal["blog_hero", "x_card", "linkedin_hero", "generic_social"]
    prompt: str
    negative_prompt: Optional[str] = None
    aspect_ratio: Literal["16:9", "9:16", "1:1", "1.91:1"]
    style_tags: List[str] = []
    seed: Optional[int] = None
    model: Optional[str] = "your-text-to-image-model"
    url: Optional[HttpUrl] = None
    alt_text: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    # Vector store metadata
    prompt_embedding_id: Optional[str] = None
    visual_similarity_score: Optional[float] = None

class Package(BaseModel):
    brief: ContentBrief
    blog: BlogArticle
    x_posts_dev: SocialPost
    x_posts_creator: SocialPost
    linkedin_posts: SocialPost
    images: List[ImageAsset]
    # Package metadata for tracking
    package_id: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    total_content_pieces: Optional[int] = None
    vector_store_ids: Optional[Dict[str, str]] = None  # Mapping of content type to vector IDs
    performance_tracking: Optional[Dict[str, Any]] = None
