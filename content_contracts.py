from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Literal

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

class BlogArticle(BaseModel):
    title: str
    slug: str
    meta_description: str
    word_count_target: int = Field(default=1500)
    body_markdown: str

class SocialPost(BaseModel):
    platform: Literal["x", "linkedin"]
    persona: Literal["developer", "creator"] = "developer"
    variants: List[str]
    suggested_hashtags: List[str]
    link_handling: str   # e.g., "add UTM", "link-in-comments"
    asset_refs: List[str] = []  # IDs or URLs for images to attach

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

class Package(BaseModel):
    brief: ContentBrief
    blog: BlogArticle
    x_posts_dev: SocialPost
    x_posts_creator: SocialPost
    linkedin_posts: SocialPost
    images: List[ImageAsset]
