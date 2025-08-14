import re
from typing import Tuple, List

BANNED_PHRASES = {
    "revolutionary", "game-changing", "magical", "100% guaranteed",
    "state-of-the-art", "best-in-class", "SOTA", "no hallucinations", "perfectly safe"
}
PROHIBITED_CLAIMS = {
    "future financial performance",
    "health/medical efficacy",
    "deceptive benchmarks",
    "benchmark superiority without public citation",
}

CREATOR_TONE_RULES = {"max_lines": 2, "max_emojis": 1}
CHAR_LIMITS = {"x": 280, "linkedin": 3000}

def input_guardrail(product_text: str) -> Tuple[bool, List[str]]:
    issues = []
    if len(product_text.strip()) < 40:
        issues.append("product input too short; add details or a URL")
    if not re.search(r"text-to-image|text to image|t2i", product_text, re.I):
        issues.append("specify text-to-image models or capabilities (t2i)")
    if not re.search(r"text-to-video|text to video|t2v", product_text, re.I):
        issues.append("specify text-to-video models or capabilities (t2v)")
    return (len(issues) == 0, issues)

def output_guardrail(blog_md: str, x_dev_variants: List[str], x_creator_variants: List[str], li_variants: List[str]) -> Tuple[bool, List[str]]:
    issues = []
    for phrase in BANNED_PHRASES:
        if re.search(rf"\b{re.escape(phrase)}\b", blog_md, flags=re.I):
            issues.append(f"Remove hype phrase: {phrase}")
    for i, v in enumerate(x_dev_variants):
        if len(v) > CHAR_LIMITS["x"]:
            issues.append(f"X (dev) variant {i+1} exceeds {CHAR_LIMITS['x']} chars")
    for i, v in enumerate(x_creator_variants):
        if len(v) > CHAR_LIMITS["x"]:
            issues.append(f"X (creator) variant {i+1} exceeds {CHAR_LIMITS['x']} chars")
        if len(v.splitlines()) > CREATOR_TONE_RULES["max_lines"]:
            issues.append(f"X (creator) variant {i+1} has too many lines")
        if v.count("😀") + v.count("🚀") + v.count("✨") + v.count("🔥") > CREATOR_TONE_RULES["max_emojis"]:
            issues.append(f"X (creator) variant {i+1} uses too many emojis")
    for claim in PROHIBITED_CLAIMS:
        if re.search(rf"\b{re.escape(claim)}\b", blog_md, flags=re.I):
            issues.append(f"Avoid prohibited claim: {claim}")
    return (len(issues) == 0, issues)
