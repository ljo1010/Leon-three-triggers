"""Regenerate the 4 priority Stansfield face cuts with gpt-image-2 for likeness/quality.
   Backs up each existing PNG to *_img1.png first (only if no backup exists yet).
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_stansfield_img2.py
"""
import os, sys, json, base64, time, shutil, urllib.request, urllib.error
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    print("ERROR: set OPENAI_API_KEY"); sys.exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "images"
LOG = OUTPUT_DIR / "_stans_img2.log"
MODEL = "gpt-image-2"

BASE = ("Film still from a 1994 neo-noir character drama set in New York City. 35mm film grain, low-key "
        "chiaroscuro lighting, cinematic letterbox composition, vignetting. Warm desaturated cream, beige and "
        "dusty olive tones. Practical tungsten/window light. No modern elements. No text, no watermarks. ")
NEG = (" Absolutely no: text, logos, watermarks, smartphones, modern vehicles, digital screens, cartoon, "
       "anime, 3D render, glossy CGI, plastic skin, oversaturation, HDR, weapons, guns, blood, gore, wounds, "
       "violence, children, minors. Do NOT depict any real or recognizable actor; original fictional faces only.")

# Shared face descriptor — matches the established stansfield_face (gpt-image-2) portrait.
STANS = ("an original fictional corrupt American official in his early forties: a gaunt pale sweat-sheened "
         "face, damp disheveled dark hair, day-old stubble, heavy-lidded glassy eyes, a rumpled dark 1990s "
         "suit with a loosened tie")

IMAGES = [
 {"filename": "stansfield_fear.png", "subject": (
    "Extreme tight close-up of " + STANS + ". His eyes go wide with dawning terror and disbelief, mouth "
    "slightly parted, fine beads of sweat on his brow. Harsh raking side light carves deep shadow across half "
    "his face; sickly warm amber-green grade. A dangerous man who has, in this final instant, finally "
    "understood his own end. Barely contained dread. Documentary realism, no glamour.")},
 {"filename": "stansfield_desk.png", "subject": (
    "Medium shot of " + STANS + " slumped back in a chair at a cluttered 1990s government office desk at "
    "night. Small wired earphones in his ears, head tilted slightly back, eyes half-closed in a heavy drugged "
    "daze. One weathered hand rests on the desk near a glass of water and a single small white pill. A harsh "
    "desk lamp rakes across his face; the rest of the room sinks into deep green-amber shadow. Stillness "
    "before a storm, contained menace.")},
 {"filename": "stansfield_wounded.png", "subject": (
    "Medium shot of " + STANS + " hunched and staggering in a dim 1990s office corridor, clutching his right "
    "forearm tight against his body, face contorted in a pained grimace through gritted teeth. Cold fury and "
    "humiliation in his eyes. Harsh overhead fluorescent light, long shadows, deep green-amber grade. No "
    "blood, nothing graphic — only the body language of sudden pain. Cinematic, restrained.")},
 {"filename": "stansfield_tony.png", "subject": (
    "Tense late-night two-shot inside a closed 1990s Little Italy Italian restaurant: red-and-white checkered "
    "tablecloths, chairs stacked upside-down on tables, dim warm tungsten wall sconces, deep shadow. On the "
    "left " + STANS + " stands looming, looking down coldly with a thin cruel half-smile. On the right, a "
    "heavyset balding Italian restaurant owner in his sixties with a careworn face sits at a table, tense and "
    "wary, hands flat on the cloth. Quiet, predatory intimidation. Documentary realism.")},
]

def log(m):
    line = f"[{time.strftime('%H:%M:%S')}] {m}"; print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f: f.write(line + "\n")

def backup(out):
    bak = out.with_name(out.stem + "_img1.png")
    if out.exists() and not bak.exists():
        shutil.copy2(out, bak); log(f"  backup -> {bak.name}")

def gen(it, i, n):
    prompt = BASE + " Subject: " + it["subject"] + NEG
    out = OUTPUT_DIR / it["filename"]
    log(f"[{i}/{n}] {MODEL} -> {it['filename']}")
    backup(out)
    payload = json.dumps({"model": MODEL, "prompt": prompt, "n": 1, "size": "1536x1024", "quality": "high"}).encode()
    for a in range(1, 3):
        req = urllib.request.Request("https://api.openai.com/v1/images/generations", data=payload,
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}, method="POST")
        s = time.time()
        try:
            with urllib.request.urlopen(req, timeout=400) as r: d = json.loads(r.read().decode())
            out.write_bytes(base64.b64decode(d["data"][0]["b64_json"]))
            log(f"[{i}/{n}] OK ({time.time()-s:.1f}s)"); return True
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', 'replace')[:400]
            log(f"[{i}/{n}] HTTP {e.code}: {body}")
            if e.code in (429, 500, 502, 503, 520) and a < 2: time.sleep(8); continue
            return False
        except Exception as e:
            log(f"[{i}/{n}] ERR {type(e).__name__}: {e}"); return False

ok = 0
for i, it in enumerate(IMAGES, 1):
    if gen(it, i, len(IMAGES)): ok += 1
    time.sleep(1)
log(f"=== Done {ok}/{len(IMAGES)} ({MODEL}) ===")
