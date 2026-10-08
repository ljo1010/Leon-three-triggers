"""Generate grenade_blast.png — a grenade detonating inside the dark apartment (Leon_17b_Hold). moderation=low.
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_grenade_blast.py
"""
import os, sys, json, base64, time, urllib.request, urllib.error
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    print("ERROR: set OPENAI_API_KEY"); sys.exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "images"
LOG = OUTPUT_DIR / "_grenade_blast.log"
MODEL = "gpt-image-2"
MOD = "low"

BASE = ("Film still from a 1994 neo-noir action thriller, interior of a dark 1990s tenement apartment at "
        "night during a raid. 35mm film grain, low-key chiaroscuro lighting, cinematic letterbox composition, "
        "vignetting. No modern elements. No text, no watermarks. ")
NEG = (" Absolutely no: text, logos, watermarks, smartphones, modern vehicles, digital screens, cartoon, "
       "anime, 3D render, glossy CGI, plastic skin, oversaturation, HDR, blood, gore, body parts, wounds, "
       "children, minors. Do NOT depict any real or recognizable actor; original fictional faces only.")

SUBJECT = (
    "The violent orange-white flash of a hand grenade detonating on the floor inside a dark, cramped tenement "
    "apartment — a blinding fireball and shockwave throwing up a burst of dust, splinters and overturned "
    "furniture, thick smoke billowing outward into the blackness. At the edge of the frame, the dark "
    "silhouette of a lean man in a long coat is hurled sideways into shadow, diving away from the blast. "
    "Chaos, a single brutal burst of light against deep darkness, debris frozen mid-air. Kinetic, cinematic, "
    "concussive. No blood, no gore, nothing graphic — only fire, smoke and flying debris.")

def log(m):
    line = f"[{time.strftime('%H:%M:%S')}] {m}"; print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f: f.write(line + "\n")

def gen():
    prompt = BASE + " Subject: " + SUBJECT + NEG
    out = OUTPUT_DIR / "grenade_blast.png"
    log(f"{MODEL} mod={MOD} -> grenade_blast.png")
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
