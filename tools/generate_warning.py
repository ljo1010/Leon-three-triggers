"""Generate leon_warning.png — the drug dealer warning scene (hotel room).
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_warning.py
"""
import os, sys, json, base64, time, urllib.request, urllib.error
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    print("ERROR: set OPENAI_API_KEY"); sys.exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "images"
LOG = OUTPUT_DIR / "_warning.log"
MODEL = "gpt-image-2"

BASE = ("Film still from a 1994 neo-noir character drama set in New York City. 35mm film grain, low-key "
        "chiaroscuro lighting, cinematic letterbox composition, vignetting. Warm desaturated cream, beige and "
        "dusty olive tones. Practical tungsten light. No modern elements. No text, no watermarks. ")
NEG = (" Absolutely no: text, logos, watermarks, smartphones, modern vehicles, digital screens, cartoon, "
       "anime, 3D render, glossy CGI, plastic skin, oversaturation, HDR, weapons, guns, knives, blood, gore, "
       "wounds, violence, children, minors. Do NOT depict any real or recognizable actor; original fictional "
       "faces only.")

SUBJECT = (
    "A dim 1990s hotel suite at night. In the center, frozen rigid in an armchair, sits a frightened heavyset "
    "sleazy drug dealer in his late forties: slicked-back dark hair, an open loud patterned silk shirt over a "
    "sweaty undershirt, beads of sweat on his wide face and double chin, eyes wide with terror, hands gripping "
    "the armrests. Looming directly behind the chair and leaning down toward his ear is the dark, backlit "
    "silhouette of a lean man in a long dark coat and a snug black knit beanie — his face entirely in shadow, "
    "no features, just a calm shape of pure menace. One warm tungsten lamp, deep shadow, breathless stillness. "
    "Nothing graphic — psychological intimidation only. Documentary realism, warm amber grade.")

def log(m):
    line = f"[{time.strftime('%H:%M:%S')}] {m}"; print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f: f.write(line + "\n")

def gen(fname, subject):
    prompt = BASE + " Subject: " + subject + NEG
    out = OUTPUT_DIR / fname
    log(f"{MODEL} -> {fname}")
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
            body = e.read().decode('utf-8', 'replace')[:400]
            log(f"HTTP {e.code}: {body}")
            if e.code in (429, 500, 502, 503, 520) and a < 2: time.sleep(8); continue
            return False
        except Exception as e:
            log(f"ERR {type(e).__name__}: {e}"); return False

gen("leon_warning.png", SUBJECT)
log("=== Done ===")
