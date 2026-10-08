"""Regenerate tony_defeated.png and tony_envelope.png to match the unified heavyset/balding Tony.
   Backs up each existing file to *_img1.png. gpt-image-2, default moderation.
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_tony_unify.py
"""
import os, sys, json, base64, time, shutil, urllib.request, urllib.error
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    print("ERROR: set OPENAI_API_KEY"); sys.exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "images"
LOG = OUTPUT_DIR / "_tony_unify.log"
MODEL = "gpt-image-2"

BASE = ("Film still from a 1994 neo-noir character drama set in a dim Little Italy restaurant, New York City. "
        "35mm film grain, low-key chiaroscuro lighting, cinematic letterbox composition, vignetting. Warm "
        "desaturated cream, beige and dusty olive tones. Practical tungsten light. No modern elements. No "
        "text, no watermarks. ")
NEG = (" Absolutely no: text, logos, watermarks, smartphones, modern vehicles, digital screens, cartoon, "
       "anime, 3D render, glossy CGI, plastic skin, oversaturation, HDR, weapons, blood, violence, children, "
       "minors. Do NOT depict any real or recognizable actor; original fictional faces only.")

TONY = ("a heavyset, balding Italian-American mob restaurant owner in his sixties with a careworn, fleshy, "
        "jowled face, thick neck and build, grey hair only at the sides, in an open-collar light shirt")

IMAGES = [
 {"filename": "tony_defeated.png", "subject": (
    "Close-up of " + TONY + ", seated at his dim restaurant table, head bowed and eyes lowered in weary, aged "
    "defeat, one heavy hand near his brow. A single warm lamp glows beside him; deep shadow all around. A "
    "powerful handler who has just, for the first time, been forced to give something up — guilt and his own "
    "age suddenly weighing on him. Documentary realism, warm amber noir, shallow depth of field.")},
 {"filename": "tony_envelope.png", "subject": (
    "Close-up of the thick, heavy hands of " + TONY + " placing a plain unmarked money envelope into an open "
    "wooden desk drawer, in his dim back office. His heavyset torso in the open-collar light shirt is partly "
    "visible above. Warm tungsten light, wine bottles and ledgers in deep shadow behind. A quiet, weighty, "
    "final gesture — money put away, not handed over. Documentary realism, warm amber, shallow depth of field.")},
]

def log(m):
    line = f"[{time.strftime('%H:%M:%S')}] {m}"; print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f: f.write(line + "\n")

def backup(out):
    bak = out.with_name(out.stem + "_img1.png")
    if out.exists() and not bak.exists():
        shutil.copy2(out, bak); log(f"  backup -> {bak.name}")

def gen(it, i, n):
    prompt = BASE + " Subject: " + it["subject"] + NEG
    out = OUTPUT_DIR / it["filename"]
    log(f"[{i}/{n}] {MODEL} -> {it['filename']}")
    backup(out)
    payload = json.dumps({"model": MODEL, "prompt": prompt, "n": 1, "size": "1536x1024", "quality": "high"}).encode()
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
