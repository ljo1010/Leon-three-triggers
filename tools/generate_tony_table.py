"""Regenerate tony_table.png with gpt-image-2 (higher fidelity, consistent Tony look).
   Backs up existing file to *_img1.png. moderation default, low fallback.
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_tony_table.py
"""
import os, sys, json, base64, time, shutil, urllib.request, urllib.error
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    print("ERROR: set OPENAI_API_KEY"); sys.exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "images"
LOG = OUTPUT_DIR / "_tony_table.log"
MODEL = "gpt-image-2"

BASE = ("Film still from a 1994 neo-noir character drama set in a dim, closed Little Italy restaurant, New "
        "York City, before opening hours. 35mm film grain, low-key chiaroscuro lighting, cinematic letterbox "
        "composition, vignetting. Warm desaturated cream, beige and dusty olive tones. Practical tungsten "
        "light. No modern elements. No text, no watermarks. ")
NEG = (" Absolutely no: text, logos, watermarks, smartphones, modern vehicles, digital screens, cartoon, "
       "anime, 3D render, glossy CGI, plastic skin, oversaturation, HDR, weapons, blood, violence, children, "
       "minors. Do NOT depict any real or recognizable actor; original fictional faces only.")

SUBJECT = (
    "Medium shot of a heavyset, balding Italian-American mob restaurant owner in his sixties — a careworn, "
    "fleshy, jowled face, thick neck and build, grey hair only at the sides, in an open-collar shirt — seated "
    "at a table with a red-and-white checkered tablecloth. A folded newspaper rests on the table near his "
    "thick, heavy hands. Behind him, shelves of wine bottles and warm tungsten wall sconces glow in deep "
    "shadow. He looks across the table with shrewd, knowing, faintly cold eyes — a handler who keeps other "
    "men's money and misses nothing. Quiet authority. Documentary realism, warm amber noir, shallow depth of "
    "field.")

def log(m):
    line = f"[{time.strftime('%H:%M:%S')}] {m}"; print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f: f.write(line + "\n")

def backup(out):
    bak = out.with_name(out.stem + "_img1.png")
    if out.exists() and not bak.exists():
        shutil.copy2(out, bak); log(f"  backup -> {bak.name}")

def attempt(moderation):
    prompt = BASE + " Subject: " + SUBJECT + NEG
    out = OUTPUT_DIR / "tony_table.png"
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

backup(OUTPUT_DIR / "tony_table.png")
for mod in [None, "low"]:
    if attempt(mod):
        log(f"=== SUCCESS moderation={mod} ==="); break
    time.sleep(2)
else:
    log("=== FAILED ===")
