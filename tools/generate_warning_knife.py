"""Generate leon_warning_knife.png — dealer warning with Leon holding a knife from behind.
   Tests moderation="low". Tries gpt-image-2 first; on a param/other rejection, falls back to gpt-image-1.
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_warning_knife.py
"""
import os, sys, json, base64, time, urllib.request, urllib.error
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    print("ERROR: set OPENAI_API_KEY"); sys.exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "images"
LOG = OUTPUT_DIR / "_warning_knife.log"

BASE = ("Film still from a 1994 neo-noir character drama set in New York City. 35mm film grain, low-key "
        "chiaroscuro lighting, cinematic letterbox composition, vignetting. Warm desaturated cream, beige and "
        "dusty olive tones. Practical tungsten light. No modern elements. No text, no watermarks. ")
# Looser negatives — still bar gore/minors, but allow the knife as a threat prop.
NEG = (" Absolutely no: text, logos, watermarks, smartphones, modern vehicles, digital screens, cartoon, "
       "anime, 3D render, glossy CGI, plastic skin, oversaturation, HDR, blood, gore, wounds, cuts, injury, "
       "children, minors. Do NOT depict any real or recognizable actor; original fictional faces only.")

SUBJECT = (
    "A dim 1990s hotel suite at night. Seated frozen and rigid in an armchair is a frightened heavyset sleazy "
    "drug dealer in his late forties: slicked-back dark hair, an open loud patterned silk shirt over a sweaty "
    "undershirt, sweat beading on his wide face, eyes wide with terror, chin lifted. Standing close behind the "
    "chair and leaning over his shoulder is a lean calm man in a long dark coat and a snug black knit beanie, "
    "his face mostly in shadow. The man holds a plain folding knife, its clean blade laid flat and still near "
    "the seated man's throat — a silent threat, the metal catching the warm lamplight. No contact, no injury, "
    "nothing graphic — pure breathless intimidation. One tungsten lamp, deep shadow, documentary realism, "
    "warm amber grade.")

def log(m):
    line = f"[{time.strftime('%H:%M:%S')}] {m}"; print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f: f.write(line + "\n")

def attempt(model, moderation):
    prompt = BASE + " Subject: " + SUBJECT + NEG
    out = OUTPUT_DIR / "leon_warning_knife.png"
    body = {"model": model, "prompt": prompt, "n": 1, "size": "1536x1024", "quality": "high"}
    if moderation:
        body["moderation"] = moderation
    payload = json.dumps(body).encode()
    log(f"try {model} moderation={moderation}")
    req = urllib.request.Request("https://api.openai.com/v1/images/generations", data=payload,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}, method="POST")
    s = time.time()
    try:
        with urllib.request.urlopen(req, timeout=400) as r: d = json.loads(r.read().decode())
        out.write_bytes(base64.b64decode(d["data"][0]["b64_json"]))
        log(f"OK ({time.time()-s:.1f}s) -> {out.name}"); return True
    except urllib.error.HTTPError as e:
        log(f"HTTP {e.code}: {e.read().decode('utf-8','replace')[:500]}"); return False
    except Exception as e:
        log(f"ERR {type(e).__name__}: {e}"); return False

# 1) gpt-image-2 with low moderation; 2) gpt-image-2 default; 3) gpt-image-1 low; 4) gpt-image-1 default
for model, mod in [("gpt-image-2", "low"), ("gpt-image-2", None),
                   ("gpt-image-1", "low"), ("gpt-image-1", None)]:
    if attempt(model, mod):
        log(f"=== SUCCESS with {model} moderation={mod} ==="); break
    time.sleep(2)
else:
    log("=== ALL ATTEMPTS FAILED ===")
