"""Generate hit_action1/2.png — Leon taking down the bodyguards (hotel hit). moderation=low.
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_hit_action.py
"""
import os, sys, json, base64, time, urllib.request, urllib.error
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    print("ERROR: set OPENAI_API_KEY"); sys.exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "images"
LOG = OUTPUT_DIR / "_hit_action.log"
MODEL = "gpt-image-2"
MOD = "low"

BASE = ("Film still from a 1994 neo-noir action thriller set in New York City. 35mm film grain, low-key "
        "chiaroscuro lighting, cinematic letterbox composition, vignetting. Warm desaturated cream, beige and "
        "dusty olive tones. Practical tungsten light, red EXIT-sign glow. No modern elements. No text, no "
        "watermarks. ")
NEG = (" Absolutely no: text, logos, watermarks, smartphones, modern vehicles, digital screens, cartoon, "
       "anime, 3D render, glossy CGI, plastic skin, oversaturation, HDR, blood, gore, wounds, injuries, "
       "children, minors. Do NOT depict any real or recognizable actor; original fictional faces only.")

LEON = ("a lean man in his late thirties in a long dark coat and a snug black knit beanie, small round dark "
        "sunglasses, light stubble — calm and precise")

IMAGES = [
 {"filename": "hit_action1.png", "subject": (
    "A smoky dim 1990s hotel suite at night. " + LEON + " steps out of deep shadow in mid-motion, a compact "
    "pistol with a long suppressor raised in a steady two-handed grip; a small muzzle flash briefly lights his "
    "determined face. Two startled bodyguards in dark suits twist toward him, caught completely off guard — "
    "one already diving for cover behind a wing-back armchair. A knocked-over lamp, drifting gunsmoke, warm "
    "tungsten light, faint red EXIT glow. Kinetic cinematic motion, shallow depth of field. Nothing graphic.")},
 {"filename": "hit_action2.png", "subject": (
    "Wide shot: " + LEON + " advances calmly through a wrecked, smoke-filled 1990s hotel suite, suppressed "
    "pistol lowered and ready at his side, stepping past two fallen bodyguards who lie still as dark shapes on "
    "the patterned carpet (no blood, no wounds, just stillness). Toppled chairs, an overturned lamp casting "
    "long shadows across the wall, red EXIT sign glow, drifting gunsmoke. Professional, unhurried menace. "
    "Cinematic wide composition, warm amber noir, deep shadow.")},
]

def log(m):
    line = f"[{time.strftime('%H:%M:%S')}] {m}"; print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f: f.write(line + "\n")

def gen(it, i, n):
    prompt = BASE + " Subject: " + it["subject"] + NEG
    out = OUTPUT_DIR / it["filename"]
    log(f"[{i}/{n}] {MODEL} mod={MOD} -> {it['filename']}")
    payload = json.dumps({"model": MODEL, "prompt": prompt, "n": 1, "size": "1536x1024",
                          "quality": "high", "moderation": MOD}).encode()
    for a in range(1, 3):
        req = urllib.request.Request("https://api.openai.com/v1/images/generations", data=payload,
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}, method="POST")
        s = time.time()
        try:
            with urllib.request.urlopen(req, timeout=400) as r: d = json.loads(r.read().decode())
            out.write_bytes(base64.b64decode(d["data"][0]["b64_json"]))
            log(f"[{i}/{n}] OK ({time.time()-s:.1f}s)"); return True
        except urllib.error.HTTPError as e:
            log(f"[{i}/{n}] HTTP {e.code}: {e.read().decode('utf-8','replace')[:400]}")
            if e.code in (429, 500, 502, 503, 520) and a < 2: time.sleep(8); continue
            return False
        except Exception as e:
            log(f"[{i}/{n}] ERR {type(e).__name__}: {e}"); return False

ok = 0
for i, it in enumerate(IMAGES, 1):
    if gen(it, i, len(IMAGES)): ok += 1
    time.sleep(1)
log(f"=== Done {ok}/{len(IMAGES)} ({MODEL} mod={MOD}) ===")
