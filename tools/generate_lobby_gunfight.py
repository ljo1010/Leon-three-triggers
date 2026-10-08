"""Generate lobby_gunfight.png — Leon's marble-lobby gunfight (Leon_13_Push). moderation=low.
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_lobby_gunfight.py
"""
import os, sys, json, base64, time, urllib.request, urllib.error
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    print("ERROR: set OPENAI_API_KEY"); sys.exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "images"
LOG = OUTPUT_DIR / "_lobby_gunfight.log"
MODEL = "gpt-image-2"
MOD = "low"

BASE = ("Film still from a 1994 neo-noir action thriller set in New York City. 35mm film grain, low-key "
        "chiaroscuro lighting, cinematic letterbox composition, vignetting. Warm desaturated cream, beige and "
        "dusty olive tones with cold window light. Practical tungsten lamps. No modern elements. No text, no "
        "watermarks. ")
NEG = (" Absolutely no: text, logos, watermarks, smartphones, modern vehicles, digital screens, cartoon, "
       "anime, 3D render, glossy CGI, plastic skin, oversaturation, HDR, blood, gore, wounds, injuries, "
       "children, minors. Do NOT depict any real or recognizable actor; original fictional faces only.")

LEON = ("a lean man in his late thirties in a long dark coat and a snug black knit beanie, light stubble, "
        "calm and precise even in motion")

SUBJECT = (
    "A grand, dim 1990s marble office-building lobby at night — tall columns, polished reflective floor, warm "
    "lamps, cold light from a wall of windows. " + LEON + " is caught mid-combat: diving and rolling low "
    "across the marble, a pistol blazing with a bright muzzle flash in his hand, spent brass casings flicking "
    "through the air around him. Several attackers in dark suits return fire from behind the columns as dark "
    "backlit silhouettes, their own muzzle flashes flaring in drifting gunsmoke. Kinetic cinematic motion "
    "blur, reflections on the marble, deep shadow. Professional, controlled violence. Nothing graphic, no "
    "blood.")

def log(m):
    line = f"[{time.strftime('%H:%M:%S')}] {m}"; print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f: f.write(line + "\n")

def gen():
    prompt = BASE + " Subject: " + SUBJECT + NEG
    out = OUTPUT_DIR / "lobby_gunfight.png"
    log(f"{MODEL} mod={MOD} -> lobby_gunfight.png")
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
