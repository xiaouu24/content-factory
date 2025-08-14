import os
from urllib.parse import urlencode, urlsplit, urlunsplit, parse_qsl
from typing import List, Dict
import httpx

# --- UTM builder ---
def build_utm(url: str, source: str, medium: str, campaign: str) -> str:
    s = urlsplit(url)
    q = dict(parse_qsl(s.query))
    q.update({
        "utm_source": source,
        "utm_medium": medium,
        "utm_campaign": campaign,
    })
    return urlunsplit((s.scheme, s.netloc, s.path, urlencode(q), s.fragment))

# --- Dummy shortener ---
BITLY_TOKEN = os.getenv("BITLY_TOKEN")

def shorten_url(url: str) -> str:
    if not BITLY_TOKEN:
        return url
    try:
        r = httpx.post(
            "https://api-ssl.bitly.com/v4/shorten",
            headers={"Authorization": f"Bearer {BITLY_TOKEN}"},
            json={"long_url": url}, timeout=15
        )
        r.raise_for_status()
        return r.json().get("link", url)
    except Exception:
        return url

# --- Code quickstarts ---
def code_quickstart(lang: str, task: str, model: str = "your-model-id") -> str:
    if lang.lower() == "python":
        if task == "text-to-image":
            return (
                "```python\nimport os, httpx\nBASE_URL = os.getenv(\"BASE_URL\", \"https://api.yourbrand.ai\")\nAPI_KEY = os.getenv(\"API_KEY\")\n\n"
                "payload = {\n  \"model\": \"%s\",\n  \"prompt\": \"Studio-lit product on matte backdrop, soft gradients\",\n  \"size\": \"1024x1024\"\n}\n\n"
                "headers = {\"Authorization\": f\"Bearer {API_KEY}\", \"Content-Type\": \"application/json\"}\n\n"
                "with httpx.Client(timeout=60) as client:\n"
                "    r = client.post(f\"{BASE_URL}/v1/images/generations\", json=payload, headers=headers)\n"
                "    r.raise_for_status()\n    print(r.json())\n```" % model
            )
        else:
            return (
                "```python\nimport os, httpx\nBASE_URL = os.getenv(\"BASE_URL\", \"https://api.yourbrand.ai\")\nAPI_KEY = os.getenv(\"API_KEY\")\n\n"
                "payload = {\n  \"model\": \"%s\",\n  \"prompt\": \"Cinematic timelapse of clouds rolling over mountains\",\n  \"duration\": 5\n}\n\n"
                "headers = {\"Authorization\": f\"Bearer {API_KEY}\", \"Content-Type\": \"application/json\"}\n\n"
                "with httpx.Client(timeout=300) as client:\n"
                "    r = client.post(f\"{BASE_URL}/v1/videos/generations\", json=payload, headers=headers)\n"
                "    r.raise_for_status()\n    print(r.json())\n```" % model
            )
    else:
        if task == "text-to-image":
            return (
                "```javascript\nconst BASE_URL = process.env.BASE_URL || \"https://api.yourbrand.ai\";\nconst API_KEY = process.env.API_KEY;\n\n"
                "const res = await fetch(`${BASE_URL}/v1/images/generations`, {\n  method: \"POST\",\n  headers: {\n    \"Authorization\": `Bearer ${API_KEY}`,\n    \"Content-Type\": \"application/json\"\n  },\n"
                "  body: JSON.stringify({\n    model: \"%s\",\n    prompt: \"Studio-lit product on matte backdrop, soft gradients\",\n    size: \"1024x1024\"\n  })\n});\n"
                "const data = await res.json();\nconsole.log(data);\n```" % model
            )
        else:
            return (
                "```javascript\nconst BASE_URL = process.env.BASE_URL || \"https://api.yourbrand.ai\";\nconst API_KEY = process.env.API_KEY;\n\n"
                "const res = await fetch(`${BASE_URL}/v1/videos/generations`, {\n  method: \"POST\",\n  headers: {\n    \"Authorization\": `Bearer ${API_KEY}`,\n    \"Content-Type\": \"application/json\"\n  },\n"
                "  body: JSON.stringify({\n    model: \"%s\",\n    prompt: \"Cinematic timelapse of clouds rolling over mountains\",\n    duration: 5\n  })\n});\n"
                "const data = await res.json();\nconsole.log(data);\n```" % model
            )

# --- Image generation via your T2I API ---
IMG_BASE_URL = os.getenv("IMG_BASE_URL", "https://api.yourbrand.ai")
IMG_MODEL = os.getenv("IMG_MODEL", "your-text-to-image-model")
IMG_API_KEY = os.getenv("API_KEY")

async def generate_brand_image(prompt: str, aspect_ratio: str = "16:9", seed: int | None = None, style_tags: List[str] | None = None, model: str | None = None) -> Dict:
    payload = {
        "model": model or IMG_MODEL,
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "seed": seed,
        "style": ", ".join(style_tags or [])
    }
    headers = {"Authorization": f"Bearer {IMG_API_KEY}", "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(f"{IMG_BASE_URL}/v1/images/generations", json=payload, headers=headers)
        r.raise_for_status()
        return r.json()

async def suggest_alt_text(prompt: str) -> str:
    return prompt[:120]

# --- Scheduler & CMS (stubs) ---
async def schedule_posts(platform: str, variants: List[str], when_iso: str, link: str | None = None) -> Dict:
    return {"platform": platform, "scheduled_for": when_iso, "count": len(variants), "link": link}

CMS_WEBHOOK = os.getenv("CMS_WEBHOOK")
async def publish_blog_md(slug: str, title: str, body_markdown: str, meta_description: str) -> Dict:
    if not CMS_WEBHOOK:
        return {"status": "skipped", "reason": "CMS_WEBHOOK not set"}
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(CMS_WEBHOOK, json={
            "slug": slug,
            "title": title,
            "markdown": body_markdown,
            "meta_description": meta_description,
        })
        return {"status": r.status_code, "text": r.text}
