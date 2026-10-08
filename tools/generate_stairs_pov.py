"""Regenerate leon_stairs.png — POV through a door gap onto Mathilda sitting on the stairwell floor.
   Backs up the existing file to *_img1.png first. Tries default moderation, then low on rejection.
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_stairs_pov.py
"""
import os, sys, json, base64, time, shutil, urllib.request, urllib.error
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    print("ERROR: set OPENAI_API_KEY"); sys.exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "images"
LOG = OUTPUT_DIR / "_stairs_pov.log"
MODEL = "gpt-image-2"

BASE = ("Film still from a 1994 neo-noir character drama set in New York City. 35mm film grain, low-key "
        "chiaroscuro lighting, cinematic letterbox composition, vignetting. Warm desaturated cream, beige and "
        "dusty olive tones. Practical tungsten light. No modern elements. No text, no watermarks. ")
NEG = (" Absolutely no: text, logos, watermarks, smartphones, modern vehicles, digital screens, cartoon, "
       "anime, 3D render, glossy CGI, plastic skin, oversaturation, HDR, weapons, blood, gore, wounds, "
       "bruises, injury, children, minors. Do NOT depict any real or recognizable actor; original fictional "
       "faces only.")

SUBJECT = (
    "POV from inside a dim apartment, looking out through the narrow vertical gap of a barely-open door. The "
    "dark edge of the door and its frame fill the left foreground in heavy shadow, a small brass security "
    "chain catching a glint. Through the bright sliver beyond, in the warm dim light of a 1990s tenement "
    "stairwell, a slight, lonely young woman in her early twenties sits hunched on the floor against the wall "
    "at the foot of the stairs. She has a neat, glossy dark bob haircut with blunt bangs and a thin black "
    "choker — a distinctive, delicate, clearly feminine look. Knees drawn up to her chest, she cradles a "
    "small carton of milk; her face is tilted gently up toward the warm light, softly lit so her bob and "
    "bangs are clearly recognizable, her expression quiet, wary and melancholy. A single bare hanging bulb "
    "glows above the stairs. Mood: observed-from-hiding, lonely. Shallow depth of field, documentary realism, "
    "warm amber palette. Nothing graphic.")

def log(m):
    line = f"[{time.strftime('%H:%M:%S')}] {m}"; print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f: f.write(line + "\n")

def backup(out):
    bak = out.with_name(out.stem + "_img1.png")
    if out.exists() and not bak.exists():
        shutil.copy2(out, bak); log(f"  backup -> {bak.name}")

def attempt(moderation):
    prompt = BASE + " Subject: " + SUBJECT + NEG
    out = OUTPUT_DIR / "leon_stairs.png"
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

backup(OUTPUT_DIR / "leon_stairs.png")
for mod in [None, "low"]:
    if attempt(mod):
        log(f"=== SUCCESS moderation={mod} ==="); break
    time.sleep(2)
else:
    log("=== FAILED ===")
