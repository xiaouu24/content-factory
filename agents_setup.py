from agents import Agent, WebSearchTool, FileSearchTool, function_tool
from content_contracts import ContentBrief, BlogArticle, SocialPost, ImageAsset
from typing import List
from tools import build_utm, shorten_url, code_quickstart, generate_brand_image, suggest_alt_text
from retrieval import retrieve_context, check_duplicate, get_style_examples, search_knowledge

# Tools → Agent SDK
build_utm_tool = function_tool(build_utm)
shorten_url_tool = function_tool(shorten_url)
code_quickstart_tool = function_tool(code_quickstart)
image_tool = function_tool(generate_brand_image)
alt_text_tool = function_tool(suggest_alt_text)

# Retrieval tools for RAG
retrieve_context_tool = function_tool(retrieve_context)
check_duplicate_tool = function_tool(check_duplicate)
get_style_examples_tool = function_tool(get_style_examples)
search_knowledge_tool = function_tool(search_knowledge)

planner = Agent(
    name="Planner",
    instructions=(
        "Create a ContentBrief for a multimodal LLM API (t2i, t2v) with segments for developers and creators. "
        "Identify models, enterprise features (SLA, SSO/SAML, data controls), pricing angles, and compliance notes. "
        "Use retrieve_context to get similar successful briefs and search_knowledge for product information."
    ),
    tools=[WebSearchTool(), retrieve_context_tool, search_knowledge_tool, check_duplicate_tool],
    output_type=ContentBrief,
)

blog_writer = Agent(
    name="Blog Writer",
    instructions=(
        "Write a technical blog (Markdown). Include model overview, Python & JS quickstarts (use code_quickstart), latency/cost examples, quality metrics with caveats, integration patterns, and Responsible AI. Include meta_description and a slug. "
        "Use get_style_examples to see high-performing blog examples and search_knowledge for technical documentation."
    ),
    tools=[code_quickstart_tool, get_style_examples_tool, search_knowledge_tool, retrieve_context_tool],
    output_type=BlogArticle,
)

x_dev_writer = Agent(
    name="X Dev Writer",
    instructions=(
        "Create up to 5 X/Twitter options (<280 chars) for developers. Each should include a concrete benefit, optional docs/demo link (use UTM + shortener), and 1–2 relevant hashtags. "
        "Use get_style_examples to see high-performing developer tweets and check_duplicate to avoid repetition."
    ),
    tools=[build_utm_tool, shorten_url_tool, get_style_examples_tool, check_duplicate_tool],
    output_type=SocialPost,
)

x_creator_writer = Agent(
    name="X Creator Writer",
    instructions=(
        "Write up to 5 X posts (<280 chars) for creators (less technical). Use hooks, plain language, optional single emoji, and a simple CTA (try/watch). Keep to 1–2 short lines. Avoid jargon. "
        "Use get_style_examples to see high-performing creator posts and check_duplicate to ensure originality."
    ),
    tools=[build_utm_tool, shorten_url_tool, get_style_examples_tool, check_duplicate_tool],
    output_type=SocialPost,
)

linkedin_writer = Agent(
    name="LinkedIn Writer",
    instructions=(
        "Create 1–2 LinkedIn variants for technical decision makers. Mention enterprise options (SLA, SSO/SAML, data controls), add 3–5 hashtags, and suggest 'link in comments' if link length hurts reach. "
        "Use get_style_examples for successful LinkedIn posts and search_knowledge for enterprise features."
    ),
    tools=[build_utm_tool, shorten_url_tool, get_style_examples_tool, search_knowledge_tool],
    output_type=SocialPost,
)

art_director = Agent(
    name="Art Director",
    instructions=(
        "Propose 2–3 on-brand image concepts as ImageAsset specs for blog_hero, x_card, and linkedin_hero. Align with brand.palette and imagery.style_tags. Include prompts, aspect ratios, optional seeds for consistency, and style_tags. "
        "Use search_knowledge to retrieve brand visual guidelines and retrieve_context for successful visual themes."
    ),
    tools=[search_knowledge_tool, retrieve_context_tool],
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
        "Act as a strict editor. Enforce tone for dev vs creator content, flag benchmark claims without citations, remove hype, and suggest precise edits. "
        "Use search_knowledge to verify style guide compliance and retrieve_context for past editorial patterns."
    ),
    tools=[search_knowledge_tool, retrieve_context_tool],
)
