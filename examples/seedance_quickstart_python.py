#!/usr/bin/env python3
"""
Seedance 1.0 quickstart (text-to-video) — Python

This script shows:
  1) text-to-video
  2) image-to-video
  3) multi-shot generation

Prereqs:
  python -m venv .venv && source .venv/bin/activate
  pip install httpx

Run:
  export API_KEY=YOUR_API_KEY
  export BASE_URL=https://api.yourbrand.ai   # or your actual base
  python examples/seedance_quickstart_python.py
"""
import os, asyncio, httpx, json

BASE_URL = os.getenv("BASE_URL", "https://api.yourbrand.ai")
API_KEY = os.getenv("API_KEY") or os.getenv("OPENAI_API_KEY")
MODEL_PRO = os.getenv("SEEDANCE_MODEL_PRO", "seedance-1.0-pro")
MODEL_LITE = os.getenv("SEEDANCE_MODEL_LITE", "seedance-1.0-lite")

def _headers():
    if not API_KEY:
        raise RuntimeError("Set API_KEY env var")
    return {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

async def text_to_video(client: httpx.AsyncClient):
    payload = {
        "model": MODEL_PRO,
        "mode": "text-to-video",
        "prompt": "Cinematic timelapse of clouds rolling over mountains, soft light",
        "duration": 5,
        "fps": 24,
        "aspect_ratio": "16:9",
        "seed": 12345
    }
    r = await client.post(f"{BASE_URL}/v1/videos/generations", json=payload, headers=_headers())
    r.raise_for_status()
    print("\n[T2V] Response:", r.json())
    return r.json()

async def image_to_video(client: httpx.AsyncClient):
    payload = {
        "model": MODEL_PRO,
        "mode": "image-to-video",
        "image_url": "https://example.com/brand-key-visual.png",
        "prompt": "Smooth parallax move, subtle camera dolly, glossy lighting",
        "duration": 5,
        "fps": 24,
        "aspect_ratio": "9:16",
        "seed": 98765
    }
    r = await client.post(f"{BASE_URL}/v1/videos/generations", json=payload, headers=_headers())
    r.raise_for_status()
    print("\n[I2V] Response:", r.json())
    return r.json()

async def multi_shot(client: httpx.AsyncClient):
    payload = {
        "model": MODEL_PRO,
        "mode": "text-to-video",
        "shots": [
            {"prompt": "Close-up of a hummingbird hovering over a flower in golden hour", "duration": 2, "seed": 555},
            {"prompt": "Pull-back to reveal a lush garden, cinematic bokeh", "duration": 3, "seed": 555}
        ],
        "fps": 24,
        "aspect_ratio": "16:9"
    }
    r = await client.post(f"{BASE_URL}/v1/videos/generations", json=payload, headers=_headers())
    r.raise_for_status()
    print("\n[Multi-shot] Response:", r.json())
    return r.json()

async def main():
    async with httpx.AsyncClient(timeout=300) as client:
        results = await asyncio.gather(
            text_to_video(client),
            image_to_video(client),
            multi_shot(client)
        )
    print("\nDone. Inspect returned job IDs / URLs:", [res.get("id") or res.get("url") for res in results])

if __name__ == "__main__":
    asyncio.run(main())
