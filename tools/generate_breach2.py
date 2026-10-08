"""Regenerate door_breach.png — Leon ambushing from the ceiling as a single officer enters (film-accurate).
   Backs up existing to *_img1.png (no-op if exists). moderation=low.
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_breach2.py
"""
import os, sys, json, base64, time, shutil, urllib.request, urllib.error
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    print("ERROR: set OPENAI_API_KEY"); sys.exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "images"
LOG = OUTPUT_DIR / "_breach2.log"
MODEL = "gpt-image-2"
MOD = "low"

BASE = ("Film still from a 1994 neo-noir thriller, interior of a dark cramped 1990s tenement apartment at "
        "night. 35mm film grain, low-key chiaroscuro lighting, cinematic letterbox composition, vignetting. "
        "Cold tactical flashlight light against warm deep shadow. No modern elements. No text, no watermarks. ")
NEG = (" Absolutely no: text, logos, watermarks, smartphones, modern vehicles, digital screens, cartoon, "
       "anime, 3D render, glossy CGI, plastic skin, oversaturation, HDR, blood, gore, wounds, children, "
       "minors, flashy action-movie hero pose, mid-air leaping. Do NOT depict any real or recognizable "
       "actor; original fictional faces only.")

SUBJECT = (
    "A single tactical police officer in helmet and body armor has just stepped cautiously through a broken, "
    "splintered doorway into the dark apartment, his flashlight beam cutting low through drifting dust as he "
    "sweeps the room — he is tense and does NOT look up. Directly above him, wedged high in the deep shadow "
    "where the wall meets the ceiling (braced silently between the door frame and the ceiling, body pressed "
    "flat to the shadows), a lean man in a long dark coat and a snug black knit beanie waits motionless, "
    "calmly aiming a pistol straight down at the unaware officer below. A patient predator's ambush — utter "
    "stillness, the held breath before violence, NOT an action pose. Claustrophobic, quiet, ominous. Cold "
    "beam light, deep darkness, shallow depth of field, documentary realism. Nothing graphic, no blood.")

def log(m):
    line = f"[{time.strftime('%H:%M:%S')}] {m}"; print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f: f.write(line + "\n")

def backup(out):
    bak = out.with_name(out.stem + "_img1.png")
    if out.exists() and not bak.exists():
        shutil.copy2(out, bak); log(f"  backup -> {bak.name}")

def gen():
    prompt = BASE + " Subject: " + SUBJECT + NEG
    out = OUTPUT_DIR / "door_breach.png"
    backup(out)
    log(f"{MODEL} mod={MOD} -> door_breach.png")
    payload = json.dumps({"model": MODEL, "prompt": prompt, "n": 1, "size": "1536x1024",
                          "quality": "high", "moderation": MOD}).encode()
    for a in range(1, 3):
        req = urllib.request.Request("https://api.openai.com/v1/images/generations", data=payload,
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}, method="POST")
        s = time.time()
        try:
            with urllib.request.urlopen(req, timeout=400) as r: d = json.loads(r.read().decode())
            out.write_bytes(base64.b64decode(d["data"][0]["b64_json"]))
            log(f"OK ({time.time()-s:.1f}s)"); return True
        except urllib.error.HTTPError as e:
            log(f"HTTP {e.code}: {e.read().decode('utf-8','replace')[:400]}")
            if e.code in (429,500,502,503,520) and a < 2: time.sleep(8); continue
            return False
        except Exception as e:
            log(f"ERR {type(e).__name__}: {e}"); return False

gen()
log("=== Done ===")
