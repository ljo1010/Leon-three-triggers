"""Regenerate school_planting — Mathilda (early 20s) planting Léon's plant at the school (ending epilogue).
Stronger Mathilda likeness + high quality (gpt-image-2)."""
import os, sys, json, base64, time, shutil
import urllib.request, urllib.error
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY: print("ERROR: no OPENAI_API_KEY"); sys.exit(1)

MODEL = "gpt-image-2"
OUTPUT_DIR = Path(__file__).parent.parent / "images"
LOG_FILE = OUTPUT_DIR / "_school_planting.log"
TARGET = OUTPUT_DIR / "school_planting.png"
BACKUP = OUTPUT_DIR / "school_planting_img1.png"

BASE = (
    "Cinematic film still from the quiet hopeful epilogue of a 1994 character drama. "
    "Shot on 35mm film with subtle grain, warm golden-hour sunlight, long soft shadows across a green lawn. "
    "Cinematic letterbox composition, shallow depth of field, tender and serene mood. "
    "Color graded with warm honey, amber and soft green tones — the warm side of a classic noir palette. "
    "Reference: the peaceful closing of Luc Besson's 1994 thriller. "
    "Natural light only. No modern elements. No text, no captions, no watermarks. "
)
NEG = (
    " Absolutely no: text overlays, logos, watermarks, signatures, smartphones, modern cars, "
    "digital screens, cartoon, anime, 3D render, glossy CGI, plastic skin, oversaturation, HDR, "
    "weapons, blood, violence, children, minors, sexualization."
)

# 마틸다 고정 디스크립터 (end_photo 등과 일관)
MATHILDA = (
    "a delicate, feminine young woman in her early twenties with a gentle, slightly melancholic face — "
    "large expressive dark eyes, soft features, a glossy dark brown chin-length bob with distinct blunt bangs cut straight across her forehead, "
    "and a thin black velvet choker around her neck. She wears a fitted ribbed knit short-sleeve top and dark trousers. "
    "Her likeness is consistent and recognizable: the same girl, now grown into a calm young woman."
)

IMAGES = [
    {
        "filename": "school_planting.png",
        "subject": (
            MATHILDA +
            " She kneels on a sunlit grass lawn, leaning forward, gently pressing the soil with both hands as she plants "
            "a single small green potted seedling (a leafy young plant) into a freshly dug hole in the earth. "
            "Her expression is quiet, focused and at peace — a private moment of closure. "
            "Behind her, softly out of focus, stands an old red-brick boarding-school manor building among large trees. "
            "Warm late-afternoon golden light rakes across the lawn. "
            "Three-quarter / medium shot, her face clearly visible and in focus. "
            "Documentary realism, natural skin, no glamour, no makeup. Warm honey, amber and green palette."
        ),
    },
]

def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f: f.write(line + "\n")

def gen(item):
    prompt = BASE + " Subject: " + item["subject"] + NEG
    out = OUTPUT_DIR / item["filename"]
    log(f"Generating ({MODEL}): {item['filename']}")
    payload = json.dumps({"model": MODEL, "prompt": prompt, "n": 1, "size": "1536x1024", "quality": "high"}).encode("utf-8")
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
        # 원본 백업(최초 1회)
        if TARGET.exists() and not BACKUP.exists():
            shutil.copy2(TARGET, BACKUP); log(f"backed up original -> {BACKUP.name}")
        out.write_bytes(png)
        log(f"OK ({time.time()-start:.1f}s, {len(png)//1024}KB) -> {out}")
        return True
    except urllib.error.HTTPError as e:
        log(f"HTTP {e.code}: {e.read().decode('utf-8', errors='replace')[:400]}")
        return False
    except Exception as e:
        log(f"ERROR: {type(e).__name__}: {e}")
        return False

ok = gen(IMAGES[0])
log("=== Done ===")
sys.exit(0 if ok else 1)
