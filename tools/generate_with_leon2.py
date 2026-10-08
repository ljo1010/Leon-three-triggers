"""Regenerate mathilda_with_leon.png — grittier, less glamorous, character-actor look (per film tone).
   Backs up existing file to *_img1.png (no-op if already backed up). moderation=low fallback.
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_with_leon2.py
"""
import os, sys, json, base64, time, shutil, urllib.request, urllib.error
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    print("ERROR: set OPENAI_API_KEY"); sys.exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "images"
LOG = OUTPUT_DIR / "_with_leon2.log"
MODEL = "gpt-image-2"

BASE = ("Film still from a 1994 neo-noir character drama set in New York City. 35mm film grain, low-key "
        "chiaroscuro lighting, cinematic letterbox composition, vignetting. Warm desaturated cream, beige and "
        "dusty olive tones. Practical tungsten light. No modern elements. No text, no watermarks. ")
# Push away from glamour.
NEG = (" Absolutely no: text, logos, watermarks, smartphones, modern vehicles, digital screens, cartoon, "
       "anime, 3D render, glossy CGI, plastic skin, oversaturation, HDR, weapons, blood, gore, children, "
       "minors, glamour, fashion-model looks, supermodel, flawless airbrushed skin, perfectly symmetrical "
       "beauty, idealized faces, beauty retouching, makeup glam. Do NOT depict any real or recognizable "
       "actor; original fictional faces only.")

SUBJECT = (
    "A dim, sparse 1990s tenement kitchen lit by a single bare pendant lamp. Two people stand a little apart, "
    "uneasy. On the left, a lean, weary HITMAN in his late thirties: a plain, weathered, ordinary face with "
    "hollow tired eyes, heavy stubble, a slightly crooked nose, short messy dark hair, deep lines — an "
    "unglamorous character-actor look, NOT handsome, in a worn shapeless beige knit sweater. On the right, a "
    "plain, ordinary young woman in her early twenties with a blunt dark bob and bangs and a thin black "
    "choker, an unremarkable everyday face (not a model, not pretty-pretty), wary and guarded, in a simple "
    "knit top. Both look worn and real, like people the camera found rather than cast for beauty. Gritty "
    "documentary realism, harsh unflattering side light, deep shadow, warm amber grade, shallow depth of "
    "field. Nothing graphic.")

def log(m):
    line = f"[{time.strftime('%H:%M:%S')}] {m}"; print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f: f.write(line + "\n")

def backup(out):
    bak = out.with_name(out.stem + "_img1.png")
    if out.exists() and not bak.exists():
        shutil.copy2(out, bak); log(f"  backup -> {bak.name}")

def attempt(moderation):
    prompt = BASE + " Subject: " + SUBJECT + NEG
    out = OUTPUT_DIR / "mathilda_with_leon.png"
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

backup(OUTPUT_DIR / "mathilda_with_leon.png")
for mod in [None, "low"]:
    if attempt(mod):
        log(f"=== SUCCESS moderation={mod} ==="); break
    time.sleep(2)
else:
    log("=== FAILED ===")
