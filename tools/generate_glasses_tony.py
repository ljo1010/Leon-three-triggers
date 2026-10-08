"""Generate leon_glasses_tony.png — Tony reflected in Leon's round sunglasses (prologue briefing).
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_glasses_tony.py
"""
import os, sys, json, base64, time, urllib.request, urllib.error
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    print("ERROR: set OPENAI_API_KEY"); sys.exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "images"
LOG = OUTPUT_DIR / "_glasses.log"
MODEL = "gpt-image-2"

BASE = ("Film still from a 1994 neo-noir character drama set in a dim Little Italy restaurant, New York City. "
        "35mm film grain, low-key chiaroscuro lighting, cinematic letterbox composition, vignetting. Warm "
        "desaturated cream, beige and dusty olive tones. Practical tungsten light. No modern elements. No "
        "text, no watermarks. ")
NEG = (" Absolutely no: text, logos, watermarks, smartphones, modern vehicles, digital screens, cartoon, "
       "anime, 3D render, glossy CGI, plastic skin, oversaturation, HDR, weapons, guns, blood, violence, "
       "children, minors. Do NOT depict any real or recognizable actor; original fictional faces only.")

SUBJECT = (
    "Tight macro close-up on the small round dark wire-frame sunglasses worn by a lean man in his late "
    "thirties (only the bridge of his nose, brow and the rims are visible, his own face mostly out of focus "
    "and in shadow around the lenses). Mirrored in the curved dark lenses, small and slightly warped, is the "
    "reflection of the man seated across the table from him: a heavyset balding Italian restaurant owner in "
    "his sixties with a careworn face, in a dark shirt, lit by a warm tungsten lamp, leaning forward as if "
    "speaking. The whole emotional weight is in that tiny reflected figure inside the lens. Extremely shallow "
    "depth of field, intimate, quiet tension, warm amber grade, documentary realism.")

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

gen("leon_glasses_tony.png", SUBJECT)
log("=== Done ===")
