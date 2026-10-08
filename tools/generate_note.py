"""Generate mathilda_note.png — the handwritten farewell note left on the table (Leon_14_ActEnd).
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_note.py
"""
import os, sys, json, base64, time, urllib.request, urllib.error
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    print("ERROR: set OPENAI_API_KEY"); sys.exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "images"
LOG = OUTPUT_DIR / "_note.log"
MODEL = "gpt-image-2"

BASE = ("Film still from a 1994 neo-noir character drama set in New York City. 35mm film grain, low-key "
        "chiaroscuro lighting, cinematic letterbox composition, vignetting. Warm desaturated cream, beige and "
        "dusty olive tones. Practical tungsten lamp light. No modern elements. ")
# Allow HANDWRITTEN english letters; bar only printed/typeset text, logos, watermarks.
NEG = (" Absolutely no: printed or typeset text, typography, fonts, captions, logos, watermarks, smartphones, "
       "modern vehicles, digital screens, cartoon, anime, 3D render, glossy CGI, plastic skin, oversaturation, "
       "HDR, weapons, blood, people, hands, children, minors.")

SUBJECT = (
    "Object-only close-up still on a worn 1990s wooden kitchen table under a warm lamp. A small torn scrap of "
    "off-white paper lies on the table; across it is written, by hand in pencil, the short English message in "
    "shaky, clumsy, uneven BLOCK CAPITAL letters (as if written by someone barely literate): "
    "\"I'M SORRY. THIS IS MY JOB.\" — the hand-printed letters crooked and childlike, clearly legible English. "
    "Beside the scrap rests a torn newspaper clipping bearing a faint grainy half-tone photo of a man's face, "
    "and a stubby worn pencil. A farewell left behind in an empty room. Deep shadow around, warm amber glow, "
    "shallow depth of field, intimate and melancholy, documentary realism.")

def log(m):
    line = f"[{time.strftime('%H:%M:%S')}] {m}"; print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f: f.write(line + "\n")

def gen():
    prompt = BASE + " Subject: " + SUBJECT + NEG
    out = OUTPUT_DIR / "mathilda_note.png"
    log(f"{MODEL} -> mathilda_note.png")
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
