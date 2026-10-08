"""Generate darkness_fight.png + leon_wounded_wall.png for Leon_17b_Hold. moderation=low.
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_hold.py
"""
import os, sys, json, base64, time, urllib.request, urllib.error
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    print("ERROR: set OPENAI_API_KEY"); sys.exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "images"
LOG = OUTPUT_DIR / "_hold.log"
MODEL = "gpt-image-2"
MOD = "low"

BASE = ("Film still from a 1994 neo-noir action thriller, interior of a dark 1990s tenement apartment at "
        "night during a police raid. 35mm film grain, low-key chiaroscuro lighting, cinematic letterbox "
        "composition, vignetting. Near-total darkness with slivers of cold light. No modern elements. No "
        "text, no watermarks. ")
NEG = (" Absolutely no: text, logos, watermarks, smartphones, modern vehicles, digital screens, cartoon, "
       "anime, 3D render, glossy CGI, plastic skin, oversaturation, HDR, blood, gore, wounds, injuries, "
       "children, minors. Do NOT depict any real or recognizable actor; original fictional faces only.")

LEON = ("a lean man in his late thirties in a long dark coat and a snug black knit beanie")

IMAGES = [
 {"filename": "darkness_fight.png", "subject": (
    "A pitch-dark, smoke-filled apartment, every lamp shattered. " + LEON + " is a fast-moving shadow flowing "
    "low along a wall, firing a pistol — a single bright muzzle flash briefly lights the drifting smoke and "
    "overturned furniture around him. Crisscrossing cold tactical flashlight beams from unseen officers slice "
    "through the blackness. He is barely visible, a ghost moving through his own home in the dark. Kinetic "
    "motion blur, overwhelming darkness pierced by light, tense and lethal. Nothing graphic, no blood.")},
 {"filename": "leon_wounded_wall.png", "subject": (
    LEON.capitalize() + " slumps back against the wall of the dark, smoke-hazed apartment, catching his "
    "ragged breath, a pistol loose in one hand, the other arm pressed across his side. His shirt is darkened "
    "and damp, his drawn face exhausted in a thin shaft of cold light. A professional who has just understood "
    "he will not survive this night, yet is utterly calm. Quiet, grim, intimate. Deep shadow, shallow depth "
    "of field, documentary realism. No visible blood or wound — only exhaustion and a dark, damp shirt.")},
]

def log(m):
    line = f"[{time.strftime('%H:%M:%S')}] {m}"; print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f: f.write(line + "\n")

def gen(it, i, n):
    prompt = BASE + " Subject: " + it["subject"] + NEG
    out = OUTPUT_DIR / it["filename"]
    log(f"[{i}/{n}] {MODEL} mod={MOD} -> {it['filename']}")
    payload = json.dumps({"model": MODEL, "prompt": prompt, "n": 1, "size": "1536x1024",
                          "quality": "high", "moderation": MOD}).encode()
    for a in range(1, 3):
        req = urllib.request.Request("https://api.openai.com/v1/images/generations", data=payload,
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}, method="POST")
        s = time.time()
        try:
            with urllib.request.urlopen(req, timeout=400) as r: d = json.loads(r.read().decode())
            out.write_bytes(base64.b64decode(d["data"][0]["b64_json"]))
            log(f"[{i}/{n}] OK ({time.time()-s:.1f}s)"); return True
        except urllib.error.HTTPError as e:
            log(f"[{i}/{n}] HTTP {e.code}: {e.read().decode('utf-8','replace')[:400]}")
            if e.code in (429,500,502,503,520) and a < 2: time.sleep(8); continue
            return False
        except Exception as e:
            log(f"[{i}/{n}] ERR {type(e).__name__}: {e}"); return False

ok = 0
for i, it in enumerate(IMAGES, 1):
    if gen(it, i, len(IMAGES)): ok += 1
    time.sleep(1)
log(f"=== Done {ok}/{len(IMAGES)} ===")
