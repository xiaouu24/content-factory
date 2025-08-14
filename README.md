# Multi-Agent Content Factory v2 (OpenAI Agent SDK)

A production-oriented starter that turns a single **product input** into:
- a technical **blog** (Markdown),
- **X/Twitter** posts (developer + creator friendly),
- **LinkedIn** posts, and
- **on-brand images** (blog hero, X card, LinkedIn hero) via your text-to-image API.

**What’s new in v2**
- Creator-friendly X posts (`x_creator_writer`) with hooks-first, ≤2 lines, ≤1 emoji.
- Visual pipeline: `art_director` proposes assets; `image_maker` calls your T2I API and adds alt text.
- Extended contracts: `images` array + persona-specific social posts.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY=...   # required for Agent SDK
# Optional:
# export BITLY_TOKEN=...     # URL shortener
# export CMS_WEBHOOK=...     # your CMS webhook
# export IMG_BASE_URL=...    # your T2I endpoint base
# export IMG_MODEL=...       # your default T2I model id
uvicorn app:app --reload --port 8000
```

### API

`POST /content-package`

```json
{
  "product_input": "Seedance 1.0 is a text-to-video API...",
  "canonical_url": "https://example.com/docs/seedance",
  "schedule_iso": null
}
```

**Response:** JSON containing a `package` with `brief`, `blog`, `x_posts_dev`, `x_posts_creator`, `linkedin_posts`, and `images`.  
If `schedule_iso` is provided, a best-effort publish stub is invoked (replace with Buffer/Hootsuite/CMS integrations).

## Files

- `style_guide.yaml` – brand voice, creator-mode rules, visual cues
- `content_contracts.py` – Pydantic models for structured outputs (incl. images)
- `tools.py` – UTM/shorten, Quickstarts, **generate_brand_image** + **suggest_alt_text**
- `guardrails.py` – input/output checks, creator tone constraints
- `agents_setup.py` – Planner, Blog Writer, X Dev Writer, **X Creator Writer**, LinkedIn Writer, **Art Director**, **Image Maker**, Editor
- `controller.py` – deterministic orchestration, guardrails, packaging
- `app.py` – FastAPI wrapper exposing `/content-package`

## Notes
- Tracing & tool wiring follow the OpenAI Agent SDK patterns.
- Replace `generate_brand_image` with your T2I API call; map return payload to `{url, width, height}`.
- Add real scheduler/CMS integrations when ready.

## License
MIT
