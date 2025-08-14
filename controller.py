import asyncio
from content_contracts import Package
from agents_setup import (
    planner, blog_writer, x_dev_writer, x_creator_writer, linkedin_writer,
    art_director, image_maker, editor
)
from agents import Runner
from guardrails import input_guardrail, output_guardrail
from tools import publish_blog_md, schedule_posts
from retrieval import RetrievalSystem
from vector_store import VectorStore
import json

async def generate_package(product_input: str, canonical_url: str | None = None) -> Package:
    ok, issues = input_guardrail(product_input)
    if not ok:
        raise ValueError(f"Input guardrail failed: {issues}")
    
    # Initialize retrieval and vector store
    retrieval = RetrievalSystem()
    vector_store = VectorStore()

    # Step A: plan
    brief_res = await Runner.run(planner, product_input)
    brief = brief_res.final_output
    if canonical_url:
        brief.canonical_url = canonical_url
    
    # Store the brief in vector store
    brief_id = retrieval.store_agent_output(
        "Planner", 
        json.dumps(brief.model_dump()),
        {"product_input": product_input, "canonical_url": canonical_url}
    )

    # Step B: writing (parallel)
    x_dev_task = Runner.run(x_dev_writer, f"persona=developer\nbrief={brief.model_dump_json()}")
    x_creator_task = Runner.run(x_creator_writer, f"persona=creator\nbrief={brief.model_dump_json()}")
    li_task = Runner.run(linkedin_writer, f"brief={brief.model_dump_json()}\nGenerate LinkedIn posts.")
    blog_task = Runner.run(blog_writer, f"brief={brief.model_dump_json()}\nWrite the blog.")

    blog, x_dev, x_creator, li = await asyncio.gather(blog_task, x_dev_task, x_creator_task, li_task)
    
    # Store generated content in vector store
    blog_id = retrieval.store_agent_output(
        "Blog Writer",
        blog.final_output.body_markdown,
        {"title": blog.final_output.title, "brief_id": brief_id}
    )
    
    # Store social posts
    for variant in x_dev.final_output.variants:
        retrieval.store_agent_output("X Dev Writer", variant, {"brief_id": brief_id, "persona": "developer"})
    
    for variant in x_creator.final_output.variants:
        retrieval.store_agent_output("X Creator Writer", variant, {"brief_id": brief_id, "persona": "creator"})
    
    for variant in li.final_output.variants:
        retrieval.store_agent_output("LinkedIn Writer", variant, {"brief_id": brief_id})

    # Step C: visuals (art direction → image generation)
    concepts = await Runner.run(art_director, f"brief={brief.model_dump_json()}")
    images = await Runner.run(image_maker, concepts.final_output)
    
    # Store image prompts
    for image in images.final_output:
        if image.prompt:
            retrieval.store_agent_output(
                "Art Director",
                image.prompt,
                {"usage": image.usage, "aspect_ratio": image.aspect_ratio, "brief_id": brief_id}
            )

    # Step D: editorial pass (optional)
    _ = await Runner.run(editor, "Review outputs for clarity & tone (dev vs creator) and visuals brand fit.")

    # Step E: guardrails
    ok, issues = output_guardrail(
        blog.final_output.body_markdown,
        x_dev.final_output.variants,
        x_creator.final_output.variants,
        li.final_output.variants,
    )
    if not ok:
        raise ValueError(f"Output guardrail failed: {issues}")

    # Create a comprehensive content package embedding for future retrieval
    package_metadata = {
        "brief_id": brief_id,
        "blog_id": blog_id,
        "product_name": brief.product_name,
        "timestamp": brief_id.split("_")[-1]  # Extract timestamp from ID
    }
    
    # Store the complete package summary
    package_summary = f"Product: {brief.product_name}\nObjective: {brief.objective}\nBlog: {blog.final_output.title}"
    vector_store.add_content("package", package_summary, package_metadata)

    return Package(
        brief=brief,
        blog=blog.final_output,
        x_posts_dev=x_dev.final_output,
        x_posts_creator=x_creator.final_output,
        linkedin_posts=li.final_output,
        images=images.final_output,
    )

async def publish_everything(pkg: Package, schedule_iso: str | None = None):
    blog_status = await publish_blog_md(
        pkg.blog.slug, pkg.blog.title, pkg.blog.body_markdown, pkg.blog.meta_description
    )
    x_status = li_status = None
    if schedule_iso:
        url = (pkg.brief.canonical_url or "").strip() or None
        x_status = await schedule_posts("x", pkg.x_posts_dev.variants + pkg.x_posts_creator.variants, schedule_iso, url)
        li_status = await schedule_posts("linkedin", pkg.linkedin_posts.variants, schedule_iso, url)
    return {"blog": blog_status, "x": x_status, "linkedin": li_status, "images": [getattr(img, "url", None) for img in pkg.images]}
