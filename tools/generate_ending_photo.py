"""Generate end_photo — warm keepsake photo of Léon + adult Mathilda smiling (우유와 화분 ending)."""
import os, sys, json, base64, time
import urllib.request, urllib.error
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY: print("ERROR: no OPENAI_API_KEY"); sys.exit(1)

MODEL = "gpt-image-2"
OUTPUT_DIR = Path(__file__).parent.parent / "images"
LOG_FILE = OUTPUT_DIR / "_end_photo.log"

BASE = (
    "Warm keepsake film photograph from the quiet hopeful epilogue of a 1994 character drama "
    "set in a small sunlit tenement apartment in New York City. "
    "Shot on 35mm film with subtle grain, soft natural window light and a gentle golden morning glow. "
    "Cinematic letterbox composition, shallow depth of field, tender and intimate mood. "
    "Color graded with warm cream, honey and soft beige tones — the warm side of a classic noir palette. "
    "Reference: cinematography of Luc Besson's 1994 thriller, but its peaceful ending. "
    "Practical lighting only — window light. No modern elements. No text, no captions, no watermarks. "
)
NEG = (
    " Absolutely no: text overlays, logos, watermarks, signatures, smartphones, modern vehicles, "
    "digital screens, cartoon, anime, 3D render, glossy CGI, plastic skin, oversaturation, HDR, "
    "weapons visible, threatening pose, menacing expression, blood, violence, children, minors."
)

IMAGES = [
    {
        "filename": "end_photo.png",
        "subject": (
            "A warm two-person keepsake portrait — both people smiling softly and genuinely toward the camera, "
            "sitting close together at a bright lace-curtained window. "
            "On the left: a lean weathered man in his late thirties, short dark hair, light stubble, "
            "kind tired eyes now warm and crinkling, a faint gentle smile, plain beige knit sweater. "
            "On the right, leaning against his shoulder: a delicate young woman in her early twenties, "
            "large bright eyes, glossy dark bob with blunt bangs, a knit top with a thin black velvet choker, "
            "a happy open natural smile. They look like a found family finally at peace together. "
            "On the windowsill beside them a small green potted plant is rooted in soil; "
            "on the table in front of them two glasses of milk catch the light. "
            "Soft golden sunlight streams through the window of a 1990s apartment. "
            "Documentary realism, candid warmth, natural skin, no glamour. "
            "Warm cream, honey and soft beige color palette."
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
    log(f"[{idx}/{total}] Generating ({MODEL}): {item['filename']}")
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
        out.write_bytes(png)
        log(f"[{idx}/{total}] OK ({time.time()-start:.1f}s, {len(png)//1024}KB) -> {out}")
        return True
    except urllib.error.HTTPError as e:
        log(f"[{idx}/{total}] HTTP {e.code}: {e.read().decode('utf-8', errors='replace')[:400]}")
        return False
    except Exception as e:
        log(f"[{idx}/{total}] ERROR: {type(e).__name__}: {e}")
        return False

ok = all(gen(it, i, len(IMAGES)) for i, it in enumerate(IMAGES, 1))
log("=== Done ===")
sys.exit(0 if ok else 1)
