"""
Retry script for the 3 images blocked by OpenAI moderation.
Strategy: no minor depictions, focus on absence/atmosphere/objects.
"""
import os
import sys
import json
import base64
import time
import urllib.request
import urllib.error
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    print("ERROR: OPENAI_API_KEY env var not set")
    sys.exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "images"
OUTPUT_DIR.mkdir(exist_ok=True)
LOG_FILE = OUTPUT_DIR / "_retry.log"

QUALITY = "high"
SIZE = "1536x1024"
MODEL = "gpt-image-1"

BASE = (
    "Film still from a 1994 neo-noir thriller set in Little Italy, New York City. "
    "Shot on 35mm film with visible grain, anamorphic lens flare, deep shadows, "
    "low-key chiaroscuro lighting. Cinematic letterbox composition, vignetting. "
    "Color graded with desaturated warm tones, crushed blacks, slightly faded highlights. "
    "Reference: cinematography of Luc Besson's 1994 film by Thierry Arbogast. "
    "Practical lighting only — tungsten bulbs, neon signs, window light. "
    "No modern elements. No text, no captions, no watermarks. "
)

NEGATIVE = (
    " Absolutely no: text overlays, logos, watermarks, signatures, modern smartphones, "
    "modern cars (post-1994), digital screens, cartoon style, anime style, 3D render look, "
    "glossy CGI, plastic skin, oversaturation, HDR look. No people visible in detail."
)

# ===== TONE-DOWNED RETRIES =====
IMAGES = [
    {
        # ORIGINAL FAIL: 12-year-old + bruised eye + flickering light
        # NEW: pure environmental, NO person visible, atmosphere of aftermath
        "filename": "mathilda_hallway.png",
        "subject": (
            "An empty, desolate 1990s NYC tenement hallway on the 4th floor. "
            "Flickering fluorescent tube light overhead casts a sickly green-tinted glow. "
            "Worn green linoleum floor with scuff marks. "
            "Door of apartment number 201 visible at the end of the hall, slightly ajar, "
            "with warm yellow light leaking out from underneath. "
            "On the stairwell landing in the foreground: a small dropped milk carton on its side, "
            "a thin trail of spilled milk on the floor. "
            "The hallway is completely empty of people. "
            "Mood: something has just happened, but no one is here. "
            "Mossy green and faded yellow color palette. "
            "Wide composition emphasizing emptiness and the vertical lines of the corridor."
        ),
    },
    {
        # ORIGINAL FAIL: view through door gap to bruised 12yo on stairs
        # NEW: silhouette from behind, no face/age, focus on stair geometry
        "filename": "leon_stairs_mathilda.png",
        "subject": (
            "A view through a narrow vertical gap in an apartment doorway, looking out into a tenement hallway. "
            "Across the hall, on a stairwell landing: a small dark silhouette of a figure seen entirely from behind, "
            "wearing a dark coat, sitting motionless on the step. Only the back of a head and shoulders visible. "
            "Strong vertical bars of the iron stair railing cast long prison-like shadows across the floor. "
            "A milk carton sits on the step beside the silhouette. "
            "Warm tungsten hallway light from a single bulb. Desaturated cream and beige palette. "
            "Voyeuristic, restrained composition. The figure's identity, age, and condition are not visible — "
            "only the abstract shape of solitude. Strong negative space."
        ),
    },
    {
        # ORIGINAL FAIL: child crouched behind fire-escape + men in suits walking away
        # NEW: pure object shot — fallen milk + retreating shoes, no observer
        "filename": "mathilda_hide.png",
        "subject": (
            "Extreme low-angle close-up of a fallen white paper milk carton on dirty concrete stairwell floor. "
            "White milk pools and spreads in a slow ribbon across the cracked concrete. "
            "In the deep, out-of-focus background: only the polished black dress shoes and dark suit trouser cuffs "
            "of two anonymous men walking away down a corridor, their backs turned, almost out of frame. "
            "The geometry of metal fire-escape stair beams creates oppressive diagonal shadows across the floor. "
            "Cold green-tinted fluorescent light from above. "
            "Shallow depth of field — focus is entirely on the milk carton in the foreground. "
            "No people in focus. No faces. Atmosphere of aftermath and witness through absence."
        ),
    },
]

def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def generate_one(item, idx, total):
    prompt = BASE + " Subject: " + item["subject"] + NEGATIVE
    out_path = OUTPUT_DIR / item["filename"]

    log(f"[{idx}/{total}] Retrying: {item['filename']}")

    payload = json.dumps({
        "model": MODEL,
        "prompt": prompt,
        "n": 1,
        "size": SIZE,
        "quality": QUALITY,
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.openai.com/v1/images/generations",
        data=payload,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        b64 = data["data"][0]["b64_json"]
        png = base64.b64decode(b64)
        out_path.write_bytes(png)
        elapsed = time.time() - start
        log(f"[{idx}/{total}] OK ({elapsed:.1f}s, {len(png)//1024}KB): {item['filename']}")
        return True
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        log(f"[{idx}/{total}] HTTP {e.code}: {err_body[:400]}")
        return False
    except Exception as e:
        log(f"[{idx}/{total}] ERROR: {type(e).__name__}: {e}")
        return False

def main():
    log(f"=== Retry batch: {len(IMAGES)} images ({QUALITY}, {SIZE}) ===")
    ok = 0
    fail = 0
    for i, item in enumerate(IMAGES, 1):
        if generate_one(item, i, len(IMAGES)):
            ok += 1
        else:
            fail += 1
        if i < len(IMAGES):
            time.sleep(2)
    log(f"=== Done. ok={ok}, fail={fail} ===")

if __name__ == "__main__":
    main()
