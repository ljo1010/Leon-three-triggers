"""Fill the 8 imageless ACT 2 branch passages.
   Policy-safe framing: hands / objects / silhouettes / POV — no weapons, no minors, no threat.
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_act2_fill.py
"""
import os, sys, json, base64, time
import urllib.request, urllib.error
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    print("ERROR: set OPENAI_API_KEY"); sys.exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "images"
LOG_FILE = OUTPUT_DIR / "_act2fill.log"

BASE = (
    "Film still from a 1994 neo-noir character drama set in Little Italy, New York City. "
    "Shot on 35mm film with subtle grain, low-key chiaroscuro lighting. "
    "Cinematic letterbox composition, vignetting. "
    "Color graded with warm desaturated cream, beige, and dusty olive tones — "
    "the warm side of classic noir palette. Reference: cinematography of Luc Besson's 1994 thriller. "
    "Practical lighting only — tungsten lamps, window light. "
    "No modern elements. No text, no captions, no watermarks. "
)
NEG = (
    " Absolutely no: text overlays, logos, watermarks, signatures, smartphones, "
    "modern vehicles, digital screens, cartoon, anime, 3D render, glossy CGI, "
    "plastic skin, oversaturation, HDR, weapons, guns, firearms, threatening pose, "
    "menacing expression, blood, violence, children, minors."
)

IMAGES = [
    {
        "filename": "leon_refuse_hands.png",
        "subject": (
            "Still-life close-up of an adult man's weathered hands resting on a dark wooden kitchen "
            "table beneath a single bare pendant lamp. The fingers are slightly tense, a folded oily "
            "cleaning cloth lies beside them. Across the table, an empty wooden chair sits in soft focus. "
            "Mood: refusal, restraint, a man holding something back. Loneliness. Shallow depth of field. "
            "Warm cream and dusty olive palette."
        ),
    },
    {
        "filename": "tony_envelope.png",
        "subject": (
            "Close-up of an older man's hands placing a plain unmarked paper envelope into an open "
            "wooden cash drawer behind a small restaurant counter. Warm tungsten light, checkered "
            "tablecloth blurred in the background, shelves of wine bottles. A quiet, final gesture. "
            "Object and hands only, no face. Shallow depth of field. Warm cream, beige, olive palette."
        ),
    },
    {
        "filename": "photo_facedown.png",
        "subject": (
            "Overhead close-up of an adult man's hand turning a small newspaper clipping face-down on a "
            "worn wooden floor lit by warm lamp light. The clipping shows only a blurred indistinct grey "
            "shape, no readable text or recognizable face. A gesture of refusal, of closing a door on "
            "revenge. Shallow depth of field. Warm desaturated palette."
        ),
    },
    {
        "filename": "leon_mathilda_window.png",
        "subject": (
            "Two backlit silhouettes seen from behind — a tall adult man and a smaller young adult woman "
            "in her early twenties — standing side by side at a tall tenement window at night, looking out "
            "at the blurred glittering city. Quiet solidarity and resolve. Their faces are not visible. "
            "Warm window glow, deep shadows in the room. Cinematic, contemplative. Dusty warm palette."
        ),
    },
    {
        "filename": "leon_confession.png",
        "subject": (
            "Tight low-key portrait of an adult man in his late thirties sitting in shadow, only half his "
            "face lit by a warm tungsten lamp from the side, eyes downcast and vulnerable. A rare moment "
            "of a guarded man opening up. Sparse 1990s apartment behind him, deep darkness. "
            "Documentary realism, no glamour, no menace. Shallow depth of field. Warm cream palette."
        ),
    },
    {
        "filename": "car_stakeout.png",
        "subject": (
            "Point-of-view from inside a parked sedan at night during a stakeout. Rain-flecked windshield "
            "in the foreground, dashboard silhouette, and across the dark street the warmly lit entrance of "
            "a stone government-style building. The passenger seat is empty. Tense, watchful stillness, "
            "no people. Reflections of streetlights on wet glass. Warm-cool noir contrast, desaturated."
        ),
    },
    {
        "filename": "radio_handoff.png",
        "subject": (
            "Close-up of two pairs of hands inside a dim car interior at night, an adult man's hand passing "
            "a small handheld two-way radio to a younger hand. Warm dashboard light, deep shadows. "
            "A moment of trust between partners. Hands and the radio only, no faces, no weapons. "
            "Shallow depth of field. Warm desaturated palette."
        ),
    },
    {
        "filename": "stairwell_escape.png",
        "subject": (
            "An empty industrial concrete emergency stairwell lit by a single caged bulb, harsh shadows on "
            "the steps. A heavy fire door stands slightly ajar at one landing, a faint elongated shadow of "
            "a person slipping through it — the figure itself barely visible. Tension, sudden quiet flight. "
            "No clear people, no violence. Cold green-grey tones bleeding into warm shadow. Cinematic."
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
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        png = base64.b64decode(data["data"][0]["b64_json"])
        out.write_bytes(png)
        log(f"[{idx}/{total}] OK ({time.time()-start:.1f}s, {len(png)//1024}KB)")
        return True
    except urllib.error.HTTPError as e:
        log(f"[{idx}/{total}] HTTP {e.code}: {e.read().decode('utf-8', errors='replace')[:400]}")
        return False
    except Exception as e:
        log(f"[{idx}/{total}] ERROR: {type(e).__name__}: {e}")
        return False

ok = 0
for i, it in enumerate(IMAGES, 1):
    if gen(it, i, len(IMAGES)): ok += 1
    time.sleep(1)
log(f"=== Done: {ok}/{len(IMAGES)} OK ===")
