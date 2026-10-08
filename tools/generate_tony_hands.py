"""Regenerate tony_hands_newspaper.png — tenser/colder tone matching the Stansfield interrogation.
   Backs up existing to *_img1.png. moderation default.
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_tony_hands.py
"""
import os, sys, json, base64, time, shutil, urllib.request, urllib.error
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    print("ERROR: set OPENAI_API_KEY"); sys.exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "images"
LOG = OUTPUT_DIR / "_tony_hands.log"
MODEL = "gpt-image-2"

BASE = ("Film still from a 1994 neo-noir thriller, a dim CLOSED Little Italy restaurant late at night. 35mm "
        "film grain, low-key chiaroscuro lighting, cinematic letterbox composition, vignetting. Cold, uneasy "
        "grade — drained desaturated tones with only a faint sickly amber-green glow, very little warmth. "
        "Practical light only. No modern elements. No text, no watermarks. ")
NEG = (" Absolutely no: text, logos, watermarks, smartphones, modern vehicles, digital screens, cartoon, "
       "anime, 3D render, glossy CGI, plastic skin, oversaturation, HDR, weapons, blood, faces, children, "
       "minors, cozy warm cheerful mood, wine glass.")

SUBJECT = (
    "Tense object-focused close-up of the thick, heavy hands of a heavyset older Italian restaurant owner, "
    "come to a sudden frozen stop, both palms flat and rigid on a folded newspaper that rests on a "
    "red-and-white checkered tablecloth. Light rolled-up shirt sleeves. The knuckles are tight, the stillness "
    "loaded with dread — a man who has just heard something he hoped never to hear. Surrounding darkness, deep "
    "shadow, the empty closed restaurant barely visible behind. No face shown. Cold, breathless, ominous. "
    "Shallow depth of field, documentary realism.")

def log(m):
    line = f"[{time.strftime('%H:%M:%S')}] {m}"; print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f: f.write(line + "\n")

def backup(out):
    bak = out.with_name(out.stem + "_img1.png")
    if out.exists() and not bak.exists():
        shutil.copy2(out, bak); log(f"  backup -> {bak.name}")

def gen():
    prompt = BASE + " Subject: " + SUBJECT + NEG
    out = OUTPUT_DIR / "tony_hands_newspaper.png"
    backup(out)
    log(f"{MODEL} -> tony_hands_newspaper.png")
    payload = json.dumps({"model": MODEL, "prompt": prompt, "n": 1, "size": "1536x1024", "quality": "high"}).encode()
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
