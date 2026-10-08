"""Regenerate scope_face.png as a practice target (anonymous jogger), per film accuracy.
   The original img1 backup is preserved (backup() is a no-op if it already exists).
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_scope_fix.py
"""
import os, sys, json, base64, time, shutil, urllib.request, urllib.error
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    print("ERROR: set OPENAI_API_KEY"); sys.exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "images"
LOG = OUTPUT_DIR / "_scope_fix.log"
MODEL = "gpt-image-2"

BASE = ("Film still from a 1994 neo-noir character drama set in New York City. 35mm film grain, low-key "
        "chiaroscuro lighting, cinematic letterbox composition, vignetting. Warm desaturated cream, beige and "
        "dusty olive tones. Practical daylight. No modern elements. No text, no watermarks. ")
NEG = (" Absolutely no: text, logos, watermarks, smartphones, modern vehicles, digital screens, cartoon, "
       "anime, 3D render, glossy CGI, plastic skin, oversaturation, HDR, weapons, guns, rifles, blood, gore, "
       "violence, children, minors. Do NOT depict any real or recognizable actor; original fictional faces only.")

IMAGES = [
 {"filename": "scope_face.png", "subject": (
    "View through a circular rifle scope: black vignette ring and a fine crosshair reticle frame the image. "
    "Centered loosely in the reticle, seen at a distance and slightly soft, is an ordinary unaware male "
    "jogger — an anonymous young adult man in a plain athletic t-shirt and shorts, mid-stride, running along "
    "a path through a sunlit green city park (Central Park feel) with blurred trees behind. A harmless "
    "stranger framed as a practice target. Bright dappled daylight, warm muted grade, documentary realism. "
    "The quiet menace is only in the crosshair, not the man.")},
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
            body = e.read().decode('utf-8', 'replace')[:400]
            log(f"[{i}/{n}] HTTP {e.code}: {body}")
            if e.code in (429, 500, 502, 503, 520) and a < 2: time.sleep(8); continue
            return False
        except Exception as e:
            log(f"[{i}/{n}] ERR {type(e).__name__}: {e}"); return False

ok = 0
for i, it in enumerate(IMAGES, 1):
    if gen(it, i, len(IMAGES)): ok += 1
log(f"=== Done {ok}/{len(IMAGES)} ({MODEL}) ===")
