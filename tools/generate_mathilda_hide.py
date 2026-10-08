"""Generate mathilda_hide_pov.png — Mathilda's POV hiding behind the stairwell as Stansfield's men emerge.
   Tries default moderation, then low on rejection.
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_mathilda_hide.py
"""
import os, sys, json, base64, time, urllib.request, urllib.error
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    print("ERROR: set OPENAI_API_KEY"); sys.exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "images"
LOG = OUTPUT_DIR / "_mathilda_hide.log"
MODEL = "gpt-image-2"

BASE = ("Film still from a 1994 neo-noir character drama set in New York City. 35mm film grain, low-key "
        "chiaroscuro lighting, cinematic letterbox composition, vignetting. Cool shadow with warm tungsten "
        "spill. Practical light only. No modern elements. No text, no watermarks. ")
NEG = (" Absolutely no: text, logos, watermarks, smartphones, modern vehicles, digital screens, cartoon, "
       "anime, 3D render, glossy CGI, plastic skin, oversaturation, HDR, weapons, guns, blood, gore, wounds, "
       "violence, children, minors. Do NOT depict any real or recognizable actor; original fictional faces only.")

SUBJECT = (
    "POV from someone hiding low behind the dark banister of a 1990s tenement stairwell. In the shadowed "
    "foreground, the vertical balusters and handrail of the staircase cut across the frame — we are crouched "
    "behind them, peering through. Beyond, down a dim hallway, an apartment door stands wide open spilling "
    "harsh light into the corridor; several menacing men in dark suits stand silhouetted in and around the "
    "lit doorway, backlit, their faces not visible. On the hallway floor in the mid-foreground a small carton "
    "of milk lies dropped on its side, a pale pool of milk spreading across the patterned tiles. Mood: frozen "
    "terror, breath held, hidden in the dark and watching. Low angle, deep shadow, mixed cold and warm light, "
    "shallow depth of field, documentary realism. Nothing graphic, no violence shown.")

def log(m):
    line = f"[{time.strftime('%H:%M:%S')}] {m}"; print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f: f.write(line + "\n")

def attempt(moderation):
    prompt = BASE + " Subject: " + SUBJECT + NEG
    out = OUTPUT_DIR / "mathilda_hide_pov.png"
    body = {"model": MODEL, "prompt": prompt, "n": 1, "size": "1536x1024", "quality": "high"}
    if moderation: body["moderation"] = moderation
    log(f"try {MODEL} moderation={moderation}")
    req = urllib.request.Request("https://api.openai.com/v1/images/generations", data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}, method="POST")
    s = time.time()
    try:
        with urllib.request.urlopen(req, timeout=400) as r: d = json.loads(r.read().decode())
        out.write_bytes(base64.b64decode(d["data"][0]["b64_json"]))
        log(f"OK ({time.time()-s:.1f}s)"); return True
    except urllib.error.HTTPError as e:
        log(f"HTTP {e.code}: {e.read().decode('utf-8','replace')[:400]}"); return False
    except Exception as e:
        log(f"ERR {type(e).__name__}: {e}"); return False

for mod in [None, "low"]:
    if attempt(mod):
        log(f"=== SUCCESS moderation={mod} ==="); break
    time.sleep(2)
else:
    log("=== FAILED ===")
