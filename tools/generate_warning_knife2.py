"""Regenerate leon_warning_knife.png — tight two-shot, Leon wearing round sunglasses, knife at throat.
   Backs up the existing file to *_img1.png first. moderation=low.
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_warning_knife2.py
"""
import os, sys, json, base64, time, shutil, urllib.request, urllib.error
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    print("ERROR: set OPENAI_API_KEY"); sys.exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "images"
LOG = OUTPUT_DIR / "_warning_knife2.log"
MODEL = "gpt-image-2"
MOD = "low"

BASE = ("Film still from a 1994 neo-noir character drama set in New York City. 35mm film grain, low-key "
        "chiaroscuro lighting, cinematic letterbox composition, vignetting. Warm desaturated cream, beige and "
        "dusty olive tones. Practical tungsten light. No modern elements. No text, no watermarks. ")
NEG = (" Absolutely no: text, logos, watermarks, smartphones, modern vehicles, digital screens, cartoon, "
       "anime, 3D render, glossy CGI, plastic skin, oversaturation, HDR, blood, gore, wounds, cuts, injury, "
       "children, minors. Do NOT depict any real or recognizable actor; original fictional faces only.")

SUBJECT = (
    "Tight, zoomed-in two-shot close-up; the two faces dominate the frame. On the right, frozen rigid, the "
    "head and shoulders of a frightened heavyset sleazy drug dealer in his late forties: slicked-back dark "
    "hair, an open loud patterned silk shirt over a sweaty undershirt, sweat beading on his wide face and "
    "double chin, eyes wide with terror, chin lifted away from the blade. Leaning in close over his shoulder "
    "from the left, filling the left of the frame, is a lean calm man in his late thirties wearing small round "
    "dark wire-frame sunglasses and a snug black knit beanie, light stubble, impassive expression, his mouth "
    "near the dealer's ear as if whispering. He holds a plain folding knife, the clean flat of the blade laid "
    "still against the side of the dealer's throat, the metal catching warm lamplight. Intimate, breathless "
    "tension. No blood, no wound, nothing graphic. One tungsten lamp, deep shadow, shallow depth of field, "
    "warm amber noir, documentary realism.")

def log(m):
    line = f"[{time.strftime('%H:%M:%S')}] {m}"; print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f: f.write(line + "\n")

def backup(out):
    bak = out.with_name(out.stem + "_img1.png")
    if out.exists() and not bak.exists():
        shutil.copy2(out, bak); log(f"  backup -> {bak.name}")

def gen(fname, subject):
    prompt = BASE + " Subject: " + subject + NEG
    out = OUTPUT_DIR / fname
    log(f"{MODEL} mod={MOD} -> {fname}")
    backup(out)
    payload = json.dumps({"model": MODEL, "prompt": prompt, "n": 1, "size": "1536x1024",
                          "quality": "high", "moderation": MOD}).encode()
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
            if e.code in (429, 500, 502, 503, 520) and a < 2: time.sleep(8); continue
            return False
        except Exception as e:
            log(f"ERR {type(e).__name__}: {e}"); return False

gen("leon_warning_knife.png", SUBJECT)
log("=== Done ===")
