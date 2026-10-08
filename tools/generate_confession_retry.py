"""Retry leon_confession.png with a softened, moderation-safe prompt.
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_confession_retry.py
"""
import os, sys, json, base64, time
import urllib.request, urllib.error
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    print("ERROR: set OPENAI_API_KEY"); sys.exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "images"

# Softer BASE: drop the "thriller" reference, lean into warm character drama / family-photo realism.
BASE = (
    "Warm, gentle film still from a 1994 character drama set in a cozy Little Italy apartment, New York City. "
    "Shot on 35mm film with soft grain and warm tungsten lamplight. "
    "Color graded with warm cream, beige and soft amber tones. "
    "Tender, quiet, hopeful mood. Practical lamp and window light only. "
    "No modern elements. No text, no captions, no watermarks. "
)
NEG = (
    " Absolutely no: text, logos, watermarks, smartphones, modern vehicles, digital screens, cartoon, "
    "anime, 3D render, glossy CGI, plastic skin, oversaturation, HDR, weapons, guns, blood, violence, "
    "children, minors, distress, crying, anything disturbing."
)

SUBJECT = (
    "A calm adult man in his late thirties sits at a small wooden kitchen table in warm lamplight, "
    "head tilted slightly down in a thoughtful, peaceful way, one weathered hand resting beside a "
    "cup of coffee. A simple beige sweater. A quiet, reflective, honest moment — a man gently sharing "
    "an old memory. Soft warm light on his face, a homely sparse apartment behind him. "
    "Documentary realism, calm and warm, no glamour. Shallow depth of field. Warm cream and amber palette."
)

prompt = BASE + " Subject: " + SUBJECT + NEG
out = OUTPUT_DIR / "leon_confession.png"
payload = json.dumps({"model":"gpt-image-1","prompt":prompt,"n":1,"size":"1536x1024","quality":"high"}).encode("utf-8")
req = urllib.request.Request(
    "https://api.openai.com/v1/images/generations",
    data=payload,
    headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    method="POST",
)
start = time.time()
try:
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    png = base64.b64decode(data["data"][0]["b64_json"])
    out.write_bytes(png)
    print(f"OK ({time.time()-start:.1f}s, {len(png)//1024}KB) -> {out.name}")
except urllib.error.HTTPError as e:
    print(f"HTTP {e.code}: {e.read().decode('utf-8', errors='replace')[:400]}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
