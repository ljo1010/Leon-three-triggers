"""Regenerate grenade_pin.png — pressing a GRENADE safety pin (not a ring) into an open palm.
   Backs up existing to *_img1.png. moderation=low.
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_grenade_pin.py
"""
import os, sys, json, base64, time, shutil, urllib.request, urllib.error
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    print("ERROR: set OPENAI_API_KEY"); sys.exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "images"
LOG = OUTPUT_DIR / "_grenade_pin.log"
MODEL = "gpt-image-2"
MOD = "low"

BASE = ("Film still from a 1994 neo-noir thriller, dim warm interior at night. 35mm film grain, low-key "
        "chiaroscuro lighting, cinematic letterbox composition, vignetting. Warm desaturated tones, deep "
        "shadow with a single sliver of light. No modern elements. No text, no watermarks. ")
NEG = (" Absolutely no: text, logos, watermarks, smartphones, modern vehicles, digital screens, cartoon, "
       "anime, 3D render, glossy CGI, plastic skin, oversaturation, HDR, blood, gore, children, minors, "
       "jewelry, wedding ring, engagement ring, gemstone, diamond, gold ring, romantic proposal. "
       "Do NOT depict any real or recognizable actor; original fictional faces only.")

SUBJECT = (
    "Extreme close-up: a weathered male hand presses a small military hand-grenade SAFETY PIN into the "
    "upturned open palm of another hand. The object is clearly a grenade pin — a dull gray steel pull-ring "
    "with its thin split cotter pin still attached, slightly bent, cold industrial metal — NOT any kind of "
    "jewelry or ring. A single sliver of warm light catches the steel; everything else sinks into deep "
    "shadow. Tense, intimate, fateful — a lethal thing handed over quietly. Shallow depth of field, "
    "documentary realism. No blood, nothing graphic.")

def log(m):
    line = f"[{time.strftime('%H:%M:%S')}] {m}"; print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f: f.write(line + "\n")

def backup(out):
    bak = out.with_name(out.stem + "_img1.png")
    if out.exists() and not bak.exists():
        shutil.copy2(out, bak); log(f"  backup -> {bak.name}")

def gen():
    prompt = BASE + " Subject: " + SUBJECT + NEG
    out = OUTPUT_DIR / "grenade_pin.png"
    backup(out)
    log(f"{MODEL} mod={MOD} -> grenade_pin.png")
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
