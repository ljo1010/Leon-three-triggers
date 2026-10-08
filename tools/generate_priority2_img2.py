"""Regenerate the 4 second-priority face cuts with gpt-image-2 for likeness/quality + consistency.
   Backs up each existing PNG to *_img1.png first (only if no backup exists yet).
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_priority2_img2.py
"""
import os, sys, json, base64, time, shutil, urllib.request, urllib.error
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    print("ERROR: set OPENAI_API_KEY"); sys.exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "images"
LOG = OUTPUT_DIR / "_p2_img2.log"
MODEL = "gpt-image-2"

BASE = ("Film still from a 1994 neo-noir character drama set in New York City. 35mm film grain, low-key "
        "chiaroscuro lighting, cinematic letterbox composition, vignetting. Warm desaturated cream, beige and "
        "dusty olive tones. Practical tungsten/window light. No modern elements. No text, no watermarks. ")
NEG = (" Absolutely no: text, logos, watermarks, smartphones, modern vehicles, digital screens, cartoon, "
       "anime, 3D render, glossy CGI, plastic skin, oversaturation, HDR, weapons, guns, rifles, blood, gore, "
       "wounds, violence, children, minors. Do NOT depict any real or recognizable actor; original fictional "
       "faces only.")

# Shared descriptors — match the established gpt-image-2 portraits.
STANS = ("an original fictional corrupt American official in his early forties: a gaunt pale sweat-sheened "
         "face, damp disheveled dark hair, day-old stubble, heavy-lidded glassy eyes, a rumpled dark 1990s "
         "suit with a loosened tie")
LEON = ("a lean solitary man in his late thirties with a weathered face, short dark hair, light stubble, "
        "quiet melancholy eyes, a plain beige knit sweater")
MATILDA = ("a delicate, clearly feminine young woman in her early twenties with large expressive eyes and a "
           "neat glossy dark bob with blunt bangs, wearing a knit top and a thin black velvet choker")

IMAGES = [
 {"filename": "scope_face.png", "subject": (
    "View through a circular rifle scope: black vignette ring and fine crosshair reticle frame the image. "
    "Centered in the reticle, slightly soft and sunlit, is the face of " + STANS + ", an unaware target seen "
    "at a distance against a blurred green sunlit city park. The cold geometry of the crosshair over a human "
    "face. Tense, morally heavy. Documentary realism, warm muted grade.")},
 {"filename": "stansfield_looms.png", "subject": (
    "Low-angle shot in a smoky dawn-lit corridor. " + STANS + " stands tall and looms, looking down with "
    "drugged, triumphant, half-lidded eyes and a faint cold smile. At the very bottom edge of the frame, the "
    "dark hunched shoulders and back of a kneeling man are barely visible in silhouette, facing away. Shafts "
    "of pale dawn light cut through haze. Menace of a victor. No blood, nothing graphic.")},
 {"filename": "mathilda_with_leon.png", "subject": (
    "Two-shot in a dim, sparse 1990s tenement kitchen lit by a single low pendant lamp. On the left, " + LEON +
    " stands quietly. On the right, slightly apart, stands " + MATILDA + ", looking toward him with a wary, "
    "searching expression. An uneasy new closeness between two solitary people. Warm amber and shadow, shallow "
    "depth of field, documentary realism.")},
 {"filename": "clipping_stansfield.png", "subject": (
    "Close-up of a single aged, torn 1990s newspaper clipping lying on a dark wood surface under a dim lamp. "
    "The clipping carries a grainy black-and-white press half-tone photo of " + STANS + " in a suit, with "
    "blurred columns of unreadable body text around it (no legible words). Yellowed paper, soft sepia tone, "
    "shallow depth of field. An object-only still — a clue prop.")},
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
