"""Generate mathilda_captured.png — Leon_16_Rescue: Stansfield gripping a defiant, cuffed (adult) Mathilda,
   seen through a glass door. moderation=low. Tries a fuller version, then a softened fallback.
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_captured.py
"""
import os, sys, json, base64, time, urllib.request, urllib.error
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    print("ERROR: set OPENAI_API_KEY"); sys.exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "images"
LOG = OUTPUT_DIR / "_captured.log"
MODEL = "gpt-image-2"
MOD = "low"

BASE = ("Film still from a 1994 neo-noir thriller set in a dim office building at night, New York City. 35mm "
        "film grain, low-key chiaroscuro lighting, cinematic letterbox composition, vignetting. Warm "
        "desaturated cream, beige and dusty olive tones, sickly amber-green grade. Practical tungsten light. "
        "No modern elements. No text, no watermarks. ")
# Looser negatives: allow a split lip / tension, still bar gore and minors.
NEG = (" Absolutely no: text, logos, watermarks, smartphones, modern vehicles, digital screens, cartoon, "
       "anime, 3D render, glossy CGI, plastic skin, oversaturation, HDR, gore, heavy bleeding, deep wounds, "
       "children, minors. Do NOT depict any real or recognizable actor; original fictional faces only.")

STANS = ("an original fictional corrupt official in his early forties: gaunt pale sweat-sheened face, damp "
         "disheveled dark hair, day-old stubble, heavy-lidded glassy drugged eyes, a rumpled dark 1990s suit "
         "with a loosened tie, a cold cruel grin")
MATILDA_ADULT = ("a defiant young woman in her early twenties (clearly an adult) with a dark bob and blunt "
                 "bangs, a small split on her lip, her wrists in handcuffs, jaw set and eyes fierce and "
                 "unbroken — refusing to look afraid")

FULL = (
    "Seen from outside through a smudged glass office door (faint reflections on the glass). Inside the dim "
    "8th-floor office, " + STANS + " stands gripping a fistful of the hair of " + MATILDA_ADULT + ", forcing "
    "her head up beside him while he turns to look out through the glass straight at the viewer with a "
    "drug-glazed smile. Tense, cruel stand-off. Deep shadow, sickly amber-green light, shallow depth of field, "
    "documentary realism. Restrained, not graphic.")

SOFT = (
    "Seen from outside through a smudged glass office door. Inside the dim 8th-floor office, " + STANS + " "
    "stands close behind " + MATILDA_ADULT + ", one hand on her shoulder, looming over her as he turns to "
    "look out through the glass at the viewer with a drug-glazed smile. She stands rigid and defiant. Tense "
    "cruel stand-off, deep shadow, sickly amber-green light, shallow depth of field, documentary realism.")

def log(m):
    line = f"[{time.strftime('%H:%M:%S')}] {m}"; print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f: f.write(line + "\n")

def attempt(label, subject):
    prompt = BASE + " Subject: " + subject + NEG
    out = OUTPUT_DIR / "mathilda_captured.png"
    log(f"try [{label}] {MODEL} mod={MOD}")
    payload = json.dumps({"model": MODEL, "prompt": prompt, "n": 1, "size": "1536x1024",
                          "quality": "high", "moderation": MOD}).encode()
    req = urllib.request.Request("https://api.openai.com/v1/images/generations", data=payload,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}, method="POST")
    s = time.time()
    try:
        with urllib.request.urlopen(req, timeout=400) as r: d = json.loads(r.read().decode())
        out.write_bytes(base64.b64decode(d["data"][0]["b64_json"]))
        log(f"OK [{label}] ({time.time()-s:.1f}s)"); return True
    except urllib.error.HTTPError as e:
        log(f"HTTP {e.code} [{label}]: {e.read().decode('utf-8','replace')[:400]}"); return False
    except Exception as e:
        log(f"ERR [{label}] {type(e).__name__}: {e}"); return False

for label, subj in [("full", FULL), ("soft", SOFT)]:
    if attempt(label, subj):
        log(f"=== SUCCESS [{label}] ==="); break
    time.sleep(3)
else:
    log("=== ALL FAILED ===")
