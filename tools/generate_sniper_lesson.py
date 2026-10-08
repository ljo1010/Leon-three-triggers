"""Regenerate sniper_lesson.png — Mathilda aiming the rifle, Leon spotting with a scope behind her.
   Backs up existing file to *_img1.png. moderation=low (rifle present).
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_sniper_lesson.py
"""
import os, sys, json, base64, time, shutil, urllib.request, urllib.error
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    print("ERROR: set OPENAI_API_KEY"); sys.exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "images"
LOG = OUTPUT_DIR / "_sniper_lesson.log"
MODEL = "gpt-image-2"
MOD = "low"

BASE = ("Film still from a 1994 neo-noir character drama set in New York City. 35mm film grain, low-key "
        "chiaroscuro lighting, cinematic letterbox composition, vignetting. Warm desaturated dusk amber tones "
        "with city light bokeh. Practical light only. No modern elements. No text, no watermarks. ")
NEG = (" Absolutely no: text, logos, watermarks, smartphones, modern vehicles, digital screens, cartoon, "
       "anime, 3D render, glossy CGI, plastic skin, oversaturation, HDR, blood, gore, wounds, injury, "
       "children, minors. Do NOT depict any real or recognizable actor; original fictional faces only.")

LEON = ("a lean man in his late thirties with a weathered face, light stubble, in a dark coat and a snug "
        "black knit beanie")
MATILDA = ("a slight, clearly feminine young woman in her early twenties with a neat dark bob and blunt bangs")

SUBJECT = (
    "A rooftop at dusk overlooking a glittering 1990s New York City skyline with distant lit skyscrapers and "
    "soft light bokeh. In the foreground, " + MATILDA + " kneels in a steady, braced shooting stance at the "
    "parapet, holding a long bolt-action sniper rifle snug to her shoulder, one eye to the scope, sighting out "
    "over the city — focused and calm. Crouched close behind her, " + LEON + " looks through a small handheld "
    "spotting scope as her spotter, his other hand resting on her shoulder to correct her posture. An open "
    "hard rifle case sits on the rooftop beside them. Mentor-and-student intimacy, quiet intensity, the city "
    "glowing below. Deep shadow, warm amber grade, shallow depth of field, documentary realism. Nothing gory.")

def log(m):
    line = f"[{time.strftime('%H:%M:%S')}] {m}"; print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f: f.write(line + "\n")

def backup(out):
    bak = out.with_name(out.stem + "_img1.png")
    if out.exists() and not bak.exists():
        shutil.copy2(out, bak); log(f"  backup -> {bak.name}")

def gen():
    prompt = BASE + " Subject: " + SUBJECT + NEG
    out = OUTPUT_DIR / "sniper_lesson.png"
    backup(out)
    log(f"{MODEL} mod={MOD} -> sniper_lesson.png")
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

gen()
log("=== Done ===")
