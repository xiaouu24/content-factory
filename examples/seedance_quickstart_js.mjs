/**
 * Seedance 1.0 quickstart (text-to-video) — Node 18+
 *
 * Shows:
 *  1) text-to-video
 *  2) image-to-video
 *  3) multi-shot
 *
 * Run:
 *   BASE_URL=https://api.yourbrand.ai API_KEY=YOUR_API_KEY node examples/seedance_quickstart_js.mjs
 */
const BASE_URL = process.env.BASE_URL || "https://api.yourbrand.ai";
const API_KEY = process.env.API_KEY || process.env.OPENAI_API_KEY;
const MODEL_PRO = process.env.SEEDANCE_MODEL_PRO || "seedance-1.0-pro";

if (!API_KEY) {
  throw new Error("Set API_KEY or OPENAI_API_KEY");
}

async function postJSON(path, body) {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${API_KEY}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify(body)
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`HTTP ${res.status}: ${text}`);
  }
  return res.json();
}

async function textToVideo() {
  const payload = {
    model: MODEL_PRO,
    mode: "text-to-video",
    prompt: "Cinematic timelapse of clouds rolling over mountains, soft light",
    duration: 5,
    fps: 24,
    aspect_ratio: "16:9",
    seed: 12345
  };
  const data = await postJSON("/v1/videos/generations", payload);
  console.log("\n[T2V] Response:", data);
  return data;
}

async function imageToVideo() {
  const payload = {
    model: MODEL_PRO,
    mode: "image-to-video",
    image_url: "https://example.com/brand-key-visual.png",
    prompt: "Smooth parallax move, subtle camera dolly, glossy lighting",
    duration: 5,
    fps: 24,
    aspect_ratio: "9:16",
    seed: 98765
  };
  const data = await postJSON("/v1/videos/generations", payload);
  console.log("\n[I2V] Response:", data);
  return data;
}

async function multiShot() {
  const payload = {
    model: MODEL_PRO,
    mode: "text-to-video",
    shots: [
      { prompt: "Close-up of a hummingbird hovering over a flower in golden hour", duration: 2, seed: 555 },
      { prompt: "Pull-back to reveal a lush garden, cinematic bokeh", duration: 3, seed: 555 }
    ],
    fps: 24,
    aspect_ratio: "16:9"
  };
  const data = await postJSON("/v1/videos/generations", payload);
  console.log("\n[Multi-shot] Response:", data);
  return data;
}

await Promise.all([textToVideo(), imageToVideo(), multiShot()])
  .then(results => {
    console.log("\nDone. Inspect returned job IDs / URLs:", results.map(r => r?.id || r?.url));
  })
  .catch(err => {
    console.error("Error:", err.message);
    process.exit(1);
  });
