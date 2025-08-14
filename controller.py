import asyncio
from content_contracts import Package
from agents_setup import (
    planner, blog_writer, x_dev_writer, x_creator_writer, linkedin_writer,
    art_director, image_maker, editor
)
from agents import Runner
from guardrails import input_guardrail, output_guardrail
from tools import publish_blog_md, schedule_posts

async def generate_package(product_input: str, canonical_url: str | None = None) -> Package:
    ok, issues = input_guardrail(product_input)
    if not ok:
        raise ValueError(f"Input guardrail failed: {issues}")

    # Step A: plan
    brief_res = await Runner.run(planner, product_input)
    brief = brief_res.final_output
    if canonical_url:
        brief.canonical_url = canonical_url

    # Step B: writing (parallel)
    x_dev_task = Runner.run(x_dev_writer, f"persona=developer\nbrief={brief.model_dump_json()}")
    x_creator_task = Runner.run(x_creator_writer, f"persona=creator\nbrief={brief.model_dump_json()}")
    li_task = Runner.run(linkedin_writer, f"brief={brief.model_dump_json()}\nGenerate LinkedIn posts.")
    blog_task = Runner.run(blog_writer, f"brief={brief.model_dump_json()}\nWrite the blog.")

    blog, x_dev, x_creator, li = await asyncio.gather(blog_task, x_dev_task, x_creator_task, li_task)

    # Step C: visuals (art direction → image generation)
    concepts = await Runner.run(art_director, f"brief={brief.model_dump_json()}")
    images = await Runner.run(image_maker, concepts.final_output)

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
