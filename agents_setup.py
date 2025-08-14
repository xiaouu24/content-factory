from agents import Agent, WebSearchTool, FileSearchTool, function_tool
from content_contracts import ContentBrief, BlogArticle, SocialPost, ImageAsset
from typing import List
from tools import build_utm, shorten_url, code_quickstart, generate_brand_image, suggest_alt_text

# Tools → Agent SDK
build_utm_tool = function_tool(build_utm)
shorten_url_tool = function_tool(shorten_url)
code_quickstart_tool = function_tool(code_quickstart)
image_tool = function_tool(generate_brand_image)
alt_text_tool = function_tool(suggest_alt_text)

planner = Agent(
    name="Planner",
    instructions=(
        "Create a ContentBrief for a multimodal LLM API (t2i, t2v) with segments for developers and creators. "
        "Identify models, enterprise features (SLA, SSO/SAML, data controls), pricing angles, and compliance notes."
    ),
    tools=[WebSearchTool(), FileSearchTool(max_num_results=4, vector_store_ids=["YOUR_VECTOR_STORE_ID"])],
    output_type=ContentBrief,
)

blog_writer = Agent(
    name="Blog Writer",
    instructions=(
        "Write a technical blog (Markdown). Include model overview, Python & JS quickstarts (use code_quickstart), latency/cost examples, quality metrics with caveats, integration patterns, and Responsible AI. Include meta_description and a slug."
    ),
    tools=[code_quickstart_tool],
    output_type=BlogArticle,
)

x_dev_writer = Agent(
    name="X Dev Writer",
    instructions=(
        "Create up to 5 X/Twitter options (<280 chars) for developers. Each should include a concrete benefit, optional docs/demo link (use UTM + shortener), and 1–2 relevant hashtags."
    ),
    tools=[build_utm_tool, shorten_url_tool],
    output_type=SocialPost,
)

x_creator_writer = Agent(
    name="X Creator Writer",
    instructions=(
        "Write up to 5 X posts (<280 chars) for creators (less technical). Use hooks, plain language, optional single emoji, and a simple CTA (try/watch). Keep to 1–2 short lines. Avoid jargon."
    ),
    tools=[build_utm_tool, shorten_url_tool],
    output_type=SocialPost,
)

linkedin_writer = Agent(
    name="LinkedIn Writer",
    instructions=(
        "Create 1–2 LinkedIn variants for technical decision makers. Mention enterprise options (SLA, SSO/SAML, data controls), add 3–5 hashtags, and suggest 'link in comments' if link length hurts reach."
    ),
    tools=[build_utm_tool, shorten_url_tool],
    output_type=SocialPost,
)

art_director = Agent(
    name="Art Director",
    instructions=(
        "Propose 2–3 on-brand image concepts as ImageAsset specs for blog_hero, x_card, and linkedin_hero. Align with brand.palette and imagery.style_tags. Include prompts, aspect ratios, optional seeds for consistency, and style_tags."
    ),
    output_type=List[ImageAsset],
)

image_maker = Agent(
    name="Image Maker",
    instructions=(
        "For each ImageAsset spec, call the image generation tool to produce an image URL. Then call alt_text tool to suggest concise alt text. Return the completed ImageAssets with URLs and alt_text."
    ),
    tools=[image_tool, alt_text_tool],
    output_type=List[ImageAsset],
)

editor = Agent(
    name="Editor",
    instructions=(
        "Act as a strict editor. Enforce tone for dev vs creator content, flag benchmark claims without citations, remove hype, and suggest precise edits."
    ),
)
