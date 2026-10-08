"""Regenerate the title image: Leon in his ICONIC look — long coat + small round
   sunglasses + black knit beanie. NO fedora, NO brimmed hat, NO trench/burberry.
   3 variants of the tenement-hallway title composition. Pick the best afterwards.
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_title.py
"""
import os, sys, json, base64, time
import urllib.request, urllib.error
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    print("ERROR: set OPENAI_API_KEY"); sys.exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "images"
LOG_FILE = OUTPUT_DIR / "_title.log"

BASE = (
    "Film still / title-card image from a 1994 neo-noir character drama set in New York City. "
    "Shot on 35mm film with subtle grain, deep low-key chiaroscuro lighting, dramatic negative space. "
    "Cinematic letterbox composition, heavy vignetting. "
    "Color graded with warm desaturated cream, amber and deep shadow tones. "
    "Practical lighting only — a bare hanging bulb, window light. "
    "No modern elements. No text, no captions, no watermarks. "
)
# Explicitly forbid the wrong costume.
NEG = (
    " Absolutely no: fedora, brimmed hat, wide-brim hat, cowboy hat, top hat, trench coat with belt, "
    "burberry coat, text overlays, logos, watermarks, signatures, smartphones, modern vehicles, "
    "digital screens, cartoon, anime, 3D render, glossy CGI, plastic skin, oversaturation, HDR, "
    "weapons, guns, blood, violence, children, minors."
)

LEON = (
    "a lone solitary man — a professional loner — wearing a long dark wool overcoat, small round dark "
    "sunglasses, and a snug BLACK KNIT WOOL BEANIE cap (rounded top, absolutely no hat brim). "
)

IMAGES = [
    {
        "filename": "title_v1.png",
        "subject": (
            LEON +
            "He stands in the center of a dim, wood-paneled 1990s tenement hallway at night, seen from "
            "a distance facing a softly glowing window at the far end. A single bare incandescent bulb "
            "hangs from the ceiling above him; a small amber transom window glows on the right wall. "
            "His backlit silhouette clearly shows the rounded knit beanie and long coat, a faint rim of "
            "light catching the round sunglasses. Mysterious, iconic, solitary title-card mood."
        ),
    },
    {
        "filename": "title_v2.png",
        "subject": (
            LEON +
            "Medium-wide shot, slightly lower camera angle, as he stands still in a shadowy tenement "
            "hallway, partially turned so a sliver of warm side light catches the round sunglasses and "
            "the edge of the knit beanie and coat collar. A bare bulb and a distant window provide the "
            "only light. Quiet menace held in stillness, deep shadow, strong title-card silhouette."
        ),
    },
    {
        "filename": "title_v3.png",
        "subject": (
            LEON +
            "Strong backlit rim-light silhouette: he stands in a narrow dark corridor with bright warm "
            "light flooding from behind, his whole outline glowing — the rounded beanie (no brim), the "
            "long coat hem, and the round sunglasses clearly readable against the glow. Cinematic, "
            "graphic, iconic poster-like negative space. Solitary and still."
        ),
    },
]

def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f: f.write(line + "\n")

def gen(item, idx, total):
    prompt = BASE + " Subject: " + item["subject"] + NEG
    out = OUTPUT_DIR / item["filename"]
    log(f"[{idx}/{total}] Generating: {item['filename']}")
    payload = json.dumps({"model":"gpt-image-1","prompt":prompt,"n":1,"size":"1536x1024","quality":"high"}).encode("utf-8")
    req = urllib.request.Request(
        "https://api.openai.com/v1/images/generations",
        data=payload,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        method="POST",
    )
    start = time.time()
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            png = base64.b64decode(data["data"][0]["b64_json"])
            out.write_bytes(png)
            log(f"[{idx}/{total}] OK ({time.time()-start:.1f}s, {len(png)//1024}KB)")
            return True
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', errors='replace')[:300]
            log(f"[{idx}/{total}] attempt {attempt}: HTTP {e.code}: {body}")
            if e.code in (500,502,503,520) and attempt < 3:
                time.sleep(5); continue
            return False
        except Exception as e:
            log(f"[{idx}/{total}] attempt {attempt}: ERROR: {type(e).__name__}: {e}")
            if attempt < 3:
                time.sleep(5); continue
            return False

ok = 0
for i, it in enumerate(IMAGES, 1):
    if gen(it, i, len(IMAGES)): ok += 1
    time.sleep(1)
log(f"=== Done: {ok}/{len(IMAGES)} OK ===")
