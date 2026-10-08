"""Generate leon_portrait — character intro shot for Leon."""
import os, sys, json, base64, time
import urllib.request, urllib.error
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY: print("ERROR"); sys.exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "images"
LOG_FILE = OUTPUT_DIR / "_one.log"

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
    "menacing expression, blood, violence."
)

IMAGES = [
    {
        "filename": "leon_portrait.png",
        "subject": (
            "Tight three-quarter character portrait of an adult man in his late thirties. "
            "Dark short hair, slight beard stubble, quiet melancholy eyes that look slightly off-camera "
            "toward a window. He wears small round dark wire-frame sunglasses pushed up on his forehead "
            "(NOT covering his eyes), a simple beige knit sweater, and a thin black leather harness over it. "
            "Average build, weathered hands visible at the bottom of frame. "
            "He sits in a sparse 1990s tenement apartment, lit only by warm tungsten lamp light from one side, "
            "the other half of his face in deep shadow. "
            "Mood: solitary, contained, the quiet of a man who has been alone too long. "
            "Not menacing, not aggressive — simply still. "
            "Shallow depth of field on his face. Documentary realism, no glamour. "
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
        log(f"[{idx}/{total}] HTTP {e.code}: {e.read().decode('utf-8', errors='replace')[:300]}")
        return False
    except Exception as e:
        log(f"[{idx}/{total}] ERROR: {type(e).__name__}: {e}")
        return False

for i, it in enumerate(IMAGES, 1):
    gen(it, i, len(IMAGES))
log("=== Done ===")
