"""Regenerate mathilda_with_leon.png back to the cleaner cinematic look (priority2 prompt).
   Does NOT touch the existing *_img1.png backup (the original gpt-image-1). moderation default.
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_with_leon_restore.py
"""
import os, sys, json, base64, time, urllib.request, urllib.error
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    print("ERROR: set OPENAI_API_KEY"); sys.exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "images"
LOG = OUTPUT_DIR / "_with_leon_restore.log"
MODEL = "gpt-image-2"

BASE = ("Film still from a 1994 neo-noir character drama set in New York City. 35mm film grain, low-key "
        "chiaroscuro lighting, cinematic letterbox composition, vignetting. Warm desaturated cream, beige and "
        "dusty olive tones. Practical tungsten/window light. No modern elements. No text, no watermarks. ")
NEG = (" Absolutely no: text, logos, watermarks, smartphones, modern vehicles, digital screens, cartoon, "
       "anime, 3D render, glossy CGI, plastic skin, oversaturation, HDR, weapons, blood, violence, children, "
       "minors. Do NOT depict any real or recognizable actor; original fictional faces only.")

LEON = ("a lean solitary man in his late thirties with a weathered face, short dark hair, light stubble, "
        "quiet melancholy eyes, a plain beige knit sweater")
MATILDA = ("a delicate, clearly feminine young woman in her early twenties with large expressive eyes and a "
           "neat glossy dark bob with blunt bangs, a knit top and a thin black velvet choker")

SUBJECT = (
    "Two-shot in a dim, sparse 1990s tenement kitchen lit by a single low pendant lamp. On the left, " + LEON +
    " stands quietly. On the right, slightly apart, stands " + MATILDA + ", looking toward him with a wary, "
    "searching expression. An uneasy new closeness between two solitary people. Warm amber and shadow, shallow "
    "depth of field, documentary realism.")

def log(m):
    line = f"[{time.strftime('%H:%M:%S')}] {m}"; print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f: f.write(line + "\n")

def gen():
    prompt = BASE + " Subject: " + SUBJECT + NEG
    out = OUTPUT_DIR / "mathilda_with_leon.png"
    log(f"{MODEL} -> mathilda_with_leon.png")
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
