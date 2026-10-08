"""Generate 4 variants for the Leon_13_Infiltration lobby ('로비. 대리석. 너무 깨끗하다.').
   Empty, pristine, trap-like — no people, no weapons. Pick the best afterwards.
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_lobby_variants.py
"""
import os, sys, json, base64, time
import urllib.request, urllib.error
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    print("ERROR: set OPENAI_API_KEY"); sys.exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "images"
LOG_FILE = OUTPUT_DIR / "_lobby.log"

BASE = (
    "Film still from a 1994 neo-noir character drama set in New York City. "
    "Shot on 35mm film with subtle grain, low-key chiaroscuro lighting. "
    "Cinematic letterbox composition, vignetting. "
    "Color graded with warm desaturated cream, beige, and dusty olive tones. "
    "Moody but readable — warm lamp pools of light, not pitch black. "
    "Practical lighting only — tungsten lamps, window light. "
    "No modern elements. No text, no captions, no watermarks. "
)
NEG = (
    " Absolutely no: text overlays, logos, watermarks, signatures, smartphones, "
    "modern vehicles, digital screens, cartoon, anime, 3D render, glossy CGI, "
    "plastic skin, oversaturation, HDR, weapons, guns, firearms, threatening pose, "
    "menacing expression, blood, violence, children, minors, people."
)

IMAGES = [
    {
        "filename": "lobby_v1.png",
        "subject": (
            "Wide symmetrical eye-level shot of a pristine marble lobby of a grand government office "
            "building at night. A row of polished brass elevator doors at center, an empty marble "
            "reception desk, tall potted palms, symmetrical leather armchairs. Warm tungsten lamp pools "
            "on a glassy reflective floor, cool moonlight from tall windows. Immaculate, silent and "
            "unnervingly empty — a deceptive calm before violence. Completely empty, no people."
        ),
    },
    {
        "filename": "lobby_v2.png",
        "subject": (
            "Point-of-view shot stepping out of a dark corridor into a brightly lit pristine marble "
            "lobby at night; the warm bright space is framed by the dark doorway edges in the "
            "foreground. Brass elevators ahead, empty armchairs, a reflective polished floor. "
            "The feeling of crossing a threshold into a quiet trap. Completely empty, no people."
        ),
    },
    {
        "filename": "lobby_v3.png",
        "subject": (
            "A vast empty marble lobby at night seen from a low dramatic angle, long shadows stretching "
            "across the polished floor from warm lamplight, tall columns, distant brass elevator doors. "
            "Utterly empty and still, an ominous calm, cinematic negative space and deep perspective. "
            "No people, no weapons."
        ),
    },
    {
        "filename": "lobby_v4.png",
        "subject": (
            "Tight cinematic shot of a pair of polished brass elevator doors in a marble lobby at night, "
            "a glowing call button reflected in the metal, a single warm wall lamp beside them, a sliver "
            "of the empty lobby mirrored in the brass surface. Tense anticipation, a sense of waiting for "
            "the doors to open. No people."
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
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            png = base64.b64decode(data["data"][0]["b64_json"])
            out.write_bytes(png)
            log(f"[{idx}/{total}] OK ({time.time()-start:.1f}s, {len(png)//1024}KB)")
            return True
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', errors='replace')[:300]
            log(f"[{idx}/{total}] attempt {attempt}: HTTP {e.code}: {body}")
            if e.code in (500,502,503,520) and attempt < 3:
                time.sleep(5); continue
            return False
        except Exception as e:
            log(f"[{idx}/{total}] attempt {attempt}: ERROR: {type(e).__name__}: {e}")
            if attempt < 3:
                time.sleep(5); continue
            return False

ok = 0
for i, it in enumerate(IMAGES, 1):
    if gen(it, i, len(IMAGES)): ok += 1
    time.sleep(1)
log(f"=== Done: {ok}/{len(IMAGES)} OK ===")
