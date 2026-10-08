"""Generate siege_street.png + door_breach.png for Leon_17_Siege. moderation=low.
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_siege.py
"""
import os, sys, json, base64, time, urllib.request, urllib.error
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    print("ERROR: set OPENAI_API_KEY"); sys.exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "images"
LOG = OUTPUT_DIR / "_siege.log"
MODEL = "gpt-image-2"
MOD = "low"

BASE = ("Film still from a 1994 neo-noir action thriller set in New York City at night. 35mm film grain, "
        "low-key chiaroscuro lighting, cinematic letterbox composition, vignetting. No modern elements (period "
        "1990s only). No text, no watermarks. ")
NEG = (" Absolutely no: text, logos, watermarks, smartphones, modern vehicles, digital screens, cartoon, "
       "anime, 3D render, glossy CGI, plastic skin, oversaturation, HDR, blood, gore, wounds, children, "
       "minors. Do NOT depict any real or recognizable actor; original fictional faces only.")

LEON = ("a lean man in his late thirties in a long dark coat and a snug black knit beanie")

IMAGES = [
 {"filename": "siege_street.png", "subject": (
    "High view down onto a narrow Little Italy street at night outside an old 1990s brick tenement building. "
    "The street below is jammed with period police cruisers and unmarked cars, their red and blue emergency "
    "lights flaring and reflecting off wet black asphalt. Dozens of silhouetted figures in tactical gear with "
    "riot shields and body armor mass toward the building's entrance through drifting haze. An overwhelming "
    "siege closing in on one building. Cold blue and red light slicing through deep shadow, cinematic wide "
    "establishing shot, tense and ominous.")},
 {"filename": "door_breach.png", "subject": (
    "Interior of a dark, cramped 1990s tenement apartment at the instant the front door bursts inward off its "
    "hinges — splintering wood, harsh white tactical flashlight beams and smoke pouring through the breach. In "
    "the foreground, backlit and calm, " + LEON + " shields a young woman behind him with one outstretched "
    "arm while raising a pistol toward the doorway with the other. Dust swirling in the cold beams, warm "
    "interior shadow behind them. Kinetic, breathless, the last stand of a cornered man. Nothing graphic, no "
    "blood.")},
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
            if e.code in (429,500,502,503,520) and a < 2: time.sleep(8); continue
            return False
        except Exception as e:
            log(f"[{i}/{n}] ERR {type(e).__name__}: {e}"); return False

ok = 0
for i, it in enumerate(IMAGES, 1):
    if gen(it, i, len(IMAGES)): ok += 1
    time.sleep(1)
log(f"=== Done {ok}/{len(IMAGES)} ===")
