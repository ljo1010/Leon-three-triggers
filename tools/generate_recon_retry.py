"""Retry recon_building.png (previous attempt hit a transient HTTP 520).
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_recon_retry.py
"""
import os, sys, json, base64, time
import urllib.request, urllib.error
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    print("ERROR: set OPENAI_API_KEY"); sys.exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "images"

BASE = (
    "Film still from a 1994 neo-noir character drama set in New York City. "
    "Shot on 35mm film with subtle grain, low-key chiaroscuro lighting. "
    "Cinematic letterbox composition, vignetting. "
    "Color graded with warm desaturated cream, beige, and dusty olive tones. "
    "Practical lighting only — tungsten lamps, window light. "
    "No modern elements. No text, no captions, no watermarks. "
)
NEG = (
    " Absolutely no: text overlays, logos, watermarks, signatures, smartphones, "
    "modern vehicles, digital screens, cartoon, anime, 3D render, glossy CGI, "
    "plastic skin, oversaturation, HDR, weapons, guns, firearms, threatening pose, "
    "menacing expression, blood, violence, children, minors."
)
SUBJECT = (
    "Establishing exterior shot at dusk of a clean, imposing stone government-style office building "
    "in New York City, seen from across a quiet wet street. Symmetrical facade, two lit entrances, "
    "tall windows glowing warm. A few anonymous blurred figures come and go at the doors. A watchful, "
    "secretive atmosphere beneath an official, respectable surface. Wet asphalt reflecting the lights. "
    "Cinematic wide shot, vignetting. Desaturated cool-warm noir palette."
)

prompt = BASE + " Subject: " + SUBJECT + NEG
out = OUTPUT_DIR / "recon_building.png"
payload = json.dumps({"model":"gpt-image-1","prompt":prompt,"n":1,"size":"1536x1024","quality":"high"}).encode("utf-8")

for attempt in range(1, 4):
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
        break
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')[:300]
        print(f"attempt {attempt}: HTTP {e.code}: {body}")
        if e.code == 520 and attempt < 3:
            time.sleep(5); continue
        break
    except Exception as e:
        print(f"attempt {attempt}: ERROR: {type(e).__name__}: {e}")
        if attempt < 3:
            time.sleep(5); continue
        break
