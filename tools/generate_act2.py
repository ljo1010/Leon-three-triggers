"""Generate essential ACT 2 images: tony_table, fallen_plant.
   Run with the key in the environment only (never hard-coded):
     OPENAI_API_KEY="sk-..." python tools/generate_act2.py
"""
import os, sys, json, base64, time
import urllib.request, urllib.error
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    print("ERROR: set OPENAI_API_KEY"); sys.exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "images"
LOG_FILE = OUTPUT_DIR / "_act2.log"

BASE = (
    "Film still from a 1994 neo-noir character drama set in Little Italy, New York City. "
    "Shot on 35mm film with subtle grain, low-key chiaroscuro lighting. "
    "Cinematic letterbox composition, vignetting. "
    "Color graded with warm desaturated cream, beige, and dusty olive tones — "
    "the warm side of classic noir palette. Reference: cinematography of Luc Besson's 1994 thriller. "
    "Practical lighting only — tungsten lamps, window light. "
    "No modern elements. No text, no captions, no watermarks. "
)
NEG = (
    " Absolutely no: text overlays, logos, watermarks, signatures, smartphones, "
    "modern vehicles, digital screens, cartoon, anime, 3D render, glossy CGI, "
    "plastic skin, oversaturation, HDR, weapons visible, threatening pose, "
    "menacing expression, blood, violence, children, minors."
)

IMAGES = [
    {
        "filename": "tony_table.png",
        "subject": (
            "Medium shot of an older Italian-American man in his early sixties seated at a worn "
            "wooden table inside a small, empty family restaurant before opening hours. "
            "Silver-grey hair combed back, a heavy tired face, reading glasses, a rumpled shirt "
            "with the sleeves rolled up. On the checkered tablecloth in front of him rest a folded "
            "newspaper and a plain unmarked paper envelope. Behind him, shelves of wine bottles and "
            "warm tungsten wall lamps glow softly. Empty chairs and stacked tables fill the background. "
            "His expression is guarded and fatherly but wary, looking calmly across the table. "
            "A quiet, tense stillness. Shallow depth of field. Documentary realism, no glamour. "
            "Warm cream, beige, dusty olive color palette."
        ),
    },
    {
        "filename": "fallen_plant.png",
        "subject": (
            "Still-life interior of an empty, sparse 1990s tenement apartment in early morning. "
            "A potted green aloe-like houseplant has been knocked over on the worn wooden floor; "
            "dark soil is spilled across the boards and the clay pot is cracked. "
            "Soft morning window light falls across the spilled soil. "
            "In the background, a small kitchen table holds a single folded blank scrap of paper "
            "(no writing of any kind). The room is completely empty of people — a heavy sense of "
            "sudden absence and quiet loss. Documentary realism, shallow depth of field. "
            "Warm cream, beige, dusty olive color palette."
        ),
    },
]

def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f: f.write(line + "\n")

def gen(item, idx, total):
    prompt = BASE + " Subject: " + item["subject"] + NEG
    out = OUTPUT_DIR / item["filename"]
    log(f"[{idx}/{total}] Generating: {item['filename']}")
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
        log(f"[{idx}/{total}] OK ({time.time()-start:.1f}s, {len(png)//1024}KB)")
        return True
    except urllib.error.HTTPError as e:
        log(f"[{idx}/{total}] HTTP {e.code}: {e.read().decode('utf-8', errors='replace')[:400]}")
        return False
    except Exception as e:
        log(f"[{idx}/{total}] ERROR: {type(e).__name__}: {e}")
        return False

for i, it in enumerate(IMAGES, 1):
    gen(it, i, len(IMAGES))
    time.sleep(1)
log("=== Done ===")
