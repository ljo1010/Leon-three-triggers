"""Replace 4 reused ACT 2 scene-images with dedicated new ones.
   Policy-safe: no people holding weapons, no minors, silhouettes/POV/exterior.
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_act2_unique.py
"""
import os, sys, json, base64, time
import urllib.request, urllib.error
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    print("ERROR: set OPENAI_API_KEY"); sys.exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "images"
LOG_FILE = OUTPUT_DIR / "_act2uniq.log"

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

IMAGES = [
    {
        "filename": "building_lobby.png",
        "subject": (
            "Wide point-of-view shot looking into the pristine marble lobby of a stately government "
            "office building at night. Polished marble floor, a row of brass elevator doors with a "
            "glowing call button, an unmanned reception desk, tall potted plants, symmetrical empty "
            "armchairs. Cold overhead light mixing with warm lamp pools. The lobby is immaculate, "
            "silent and unnervingly empty — a deceptive calm, the feeling of a quiet trap waiting. "
            "No people. Cinematic depth, vignetting. Desaturated cream and grey-green palette."
        ),
    },
    {
        "filename": "lobby_aftermath.png",
        "subject": (
            "A grand marble building lobby moments after a sudden event, a thin pale haze of smoke "
            "drifting and slowly clearing in shafts of lamplight. An overturned armchair and scattered "
            "papers on the polished floor. In the middle distance, the lone dark silhouette of a man in "
            "a long coat stands still, seen from behind, weary and drained. A quiet, hollow aftermath. "
            "No blood, no visible weapon, no other people. Atmospheric haze, deep shadows. "
            "Desaturated warm-grey palette, cinematic."
        ),
    },
    {
        "filename": "mathilda_resolve.png",
        "subject": (
            "A young woman in her early twenties kneels on the worn wooden floor of a dim 1990s "
            "apartment, lit by a single warm lamp. Short dark bobbed hair. She looks down with quiet, "
            "cold, focused determination — no tears — at a small newspaper clipping lying on the "
            "floorboards (the clipping shows only a blurred indistinct grey shape, no readable text or "
            "face). Grief turned to stone, a resolve hardening. Documentary realism, shallow depth of "
            "field. Warm cream and amber palette."
        ),
    },
    {
        "filename": "recon_building.png",
        "subject": (
            "Establishing exterior shot at dusk of a clean, imposing stone government-style office "
            "building in New York City, seen from across a quiet wet street. Symmetrical facade, two "
            "lit entrances, tall windows glowing warm. A few anonymous blurred figures come and go at "
            "the doors. A watchful, secretive atmosphere beneath an official, respectable surface. "
            "Wet asphalt reflecting the lights. Cinematic wide shot, vignetting. "
            "Desaturated cool-warm noir palette."
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

ok = 0
for i, it in enumerate(IMAGES, 1):
    if gen(it, i, len(IMAGES)): ok += 1
    time.sleep(1)
log(f"=== Done: {ok}/{len(IMAGES)} OK ===")
