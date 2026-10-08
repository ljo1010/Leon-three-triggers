"""
Round 2: 15 additional images for deeper immersion.
Lessons learned: no minor depictions, no implied violence to minors,
absence/silhouette/POV/object focus.
"""
import os, sys, json, base64, time
import urllib.request, urllib.error
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    print("ERROR: OPENAI_API_KEY env var not set"); sys.exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "images"
OUTPUT_DIR.mkdir(exist_ok=True)
LOG_FILE = OUTPUT_DIR / "_more.log"

QUALITY = "high"
SIZE = "1536x1024"
MODEL = "gpt-image-1"

BASE = (
    "Film still from a 1994 neo-noir thriller set in Little Italy, New York City. "
    "Shot on 35mm film with visible grain, anamorphic lens flare, deep shadows, "
    "low-key chiaroscuro lighting. Cinematic letterbox composition, vignetting. "
    "Color graded with desaturated warm tones, crushed blacks, slightly faded highlights. "
    "Reference: cinematography of Luc Besson's 1994 thriller by Thierry Arbogast. "
    "Practical lighting only — tungsten bulbs, neon signs, window light. "
    "No modern elements. No text, no captions, no watermarks. "
)
NEG = (
    " Absolutely no: text overlays, logos, watermarks, signatures, modern smartphones, "
    "modern cars (post-1994), digital screens, cartoon style, anime style, 3D render look, "
    "glossy CGI, plastic skin, oversaturation, HDR look."
)

# POV palettes
PAL_LEON = "Color palette dominated by warm cream, beige, dusty olive. "
PAL_MATH = "Color palette dominated by mossy green, dusty rose, faded yellows. "
PAL_STAN = "Color palette dominated by sickly purple, fluorescent magenta, cold cyan shadows. "

IMAGES = [
    # === LEON 시점 추가 ===
    {
        "filename": "leon_dawn_walk.png",
        "subject": (
            PAL_LEON +
            "Wide cinematic shot of a lone tall silhouette of an adult man in a long dark coat walking down "
            "an empty cobblestone street in Little Italy, NYC, at 4am. Holding a single paper milk carton. "
            "The street is wet from earlier rain, reflecting the warm tungsten of streetlamps and a distant "
            "neon pizzeria sign. Steam rises from a manhole. No other people. Long shadows stretch toward camera. "
            "Composition: tiny figure dwarfed by tall tenement buildings on either side. Anamorphic widescreen feel."
        ),
    },
    {
        "filename": "leon_plant_hands.png",
        "subject": (
            PAL_LEON +
            "Extreme close-up macro: a pair of large, calloused adult male hands gently wiping the broad green "
            "leaves of a houseplant with a soft white cloth. Sunlight from a window catches the dust motes in the air. "
            "One finger has a small scar across the knuckle. The contrast is striking: rough hands, delicate plant. "
            "Shallow depth of field. Tender ritual. Background dark and out of focus."
        ),
    },
    {
        "filename": "leon_open_ending.png",
        "subject": (
            PAL_LEON +
            "End of Act 1 climactic shot. From inside a dim apartment looking toward the front door, "
            "which has just opened. The doorway is filled with bright warm yellow hallway light, "
            "blowing out into a halo. A small dark backlit silhouette stands in the doorway, just an outline — "
            "we cannot see their face, age, or condition, only the shape of a figure entering. "
            "In the foreground, slightly out of focus, the silhouette of an adult man with his back to camera "
            "watches from the shadows. A houseplant visible on a small table. "
            "Composition: pure backlight contrast, the doorway as a portal of light. Emotional weight: a threshold crossed."
        ),
    },
    {
        "filename": "leon_closed_aftermath.png",
        "subject": (
            PAL_LEON +
            "An empty 1990s tenement apartment, viewed from low angle. In the foreground, slightly out of focus, "
            "a small potted plant on a windowsill — its leaves are gently shaking, as if disturbed by a breath. "
            "In the mid-ground: a single empty wooden chair. The morning light through gauze curtains is harsh and pale. "
            "The room is utterly still. Faint dust hangs in the light shafts. "
            "Mood: aftermath, regret, the heaviness of an absence. No people. Negative space dominates."
        ),
    },
    {
        "filename": "leon_eye_memory.png",
        "subject": (
            PAL_LEON +
            "Extreme macro close-up of a single adult human eye. The iris is a soft hazel-green, slightly wet. "
            "Reflected in the pupil: the blurry shape of a window with morning light. Subtle wrinkles at the corner. "
            "The eye is half-shadowed, the other half lit by warm window light. "
            "Mood: a long-buried memory surfacing. Highly shallow depth of field — only the iris is in focus. "
            "Pure stillness. The expression is unreadable — neither sad nor happy, just present."
        ),
    },
    # === MATHILDA 시점 추가 ===
    {
        "filename": "mathilda_street.png",
        "subject": (
            PAL_MATH +
            "Low-angle subjective POV shot from sidewalk level. A bright 1990s NYC street in harsh midday sun, "
            "overexposed and washed out. In the foreground: a pair of small worn black sneakers and bare scraped "
            "knees frozen mid-step on a dirty sidewalk. In the blurred background: the legs and torsos of "
            "anonymous adult pedestrians walking past, indifferent — only their bodies from waist down visible, "
            "no faces. A yellow taxi blurred at the edge of frame. A dropped milk carton on the curb. "
            "Mood: disorientation, alienation, the world too bright and indifferent."
        ),
    },
    {
        "filename": "mathilda_lookup_building.png",
        "subject": (
            PAL_MATH +
            "Extreme low-angle upward shot of a 1990s NYC tenement apartment building, looking straight up "
            "the brick facade toward the sky. Iron fire escapes zigzag up the building. One window on an upper "
            "floor is faintly lit, warm yellow. The sky above is overcast, pale. Pigeons circle in the corner of frame. "
            "Mood: smallness, return, the building looms like a cliff. Vertigo perspective. No people visible."
        ),
    },
    # === 환경 / ESTABLISHING ===
    {
        "filename": "nyc_little_italy.png",
        "subject": (
            "Wide establishing shot of a 1994 Little Italy NYC street at twilight. Narrow road lined with old "
            "brick tenements, fire escapes, faded Italian restaurant signs in red and green neon. Steam rising "
            "from a manhole. A few parked vintage 1980s sedans. String lights crossing the street. "
            "Anamorphic widescreen composition, deep perspective vanishing point. "
            "Desaturated warm tones, period-accurate, cinematic. A few distant blurred pedestrians. No modern elements."
        ),
    },
    {
        "filename": "nyc_dawn.png",
        "subject": (
            "Wide aerial-style cinematic shot of pre-dawn NYC, deep blue sky just turning pink at the horizon. "
            "Manhattan skyline silhouetted, World Trade Center towers visible. A solitary milk delivery truck "
            "moving down an empty avenue, headlights cutting through morning mist. Steam rising from city grates. "
            "Mood: the city is sleeping. Composition: vast and quiet, the city as a sleeping animal. Period: 1994."
        ),
    },
    {
        "filename": "italian_restaurant.png",
        "subject": (
            "Interior of a dim 1994 Little Italy Italian restaurant at night. Empty checkered tablecloths, "
            "wine bottles in straw baskets, red leather booths. A single candle burning on one table. "
            "Old framed family photos on the brick walls. A vintage espresso machine in the background. "
            "Warm tungsten light, deep red color palette with green accents. Cigarette smoke hangs in the air. "
            "An empty wooden chair at the head of one table, slightly pulled out, as if someone just left. "
            "Mood: clandestine meeting place, before something happens. No people visible."
        ),
    },
    # === ACT 2 / 분위기 ===
    {
        "filename": "training_silhouette.png",
        "subject": (
            PAL_LEON +
            "Silhouette of an adult man's hands seen from behind, methodically assembling a disassembled Beretta "
            "92FS pistol on a clean white cloth, at a wooden kitchen table. Single overhead pendant lamp casts "
            "a hard cone of light directly on the table, while the rest of the room is in darkness. "
            "Tools laid out with surgical precision — cleaning rod, oil, brush. "
            "Composition: hands and weapon are the only thing visible. Body is silhouetted against the void. "
            "Mood: ritual, discipline, the calm before. No face visible."
        ),
    },
    {
        "filename": "cigarette_window.png",
        "subject": (
            "Close-up of a smoldering cigarette resting on the edge of a clear glass ashtray on a windowsill. "
            "Smoke curls upward into a shaft of pale morning light from a window with iron security bars. "
            "The window overlooks a brick wall across the air shaft. Out of focus in the background: "
            "an empty mug, peeling paint, a folded newspaper. Mood: insomnia, waiting, the long pause between events. "
            "Desaturated, contemplative. Shallow depth of field on the ember."
        ),
    },
    {
        "filename": "rain_window.png",
        "subject": (
            "Close-up of a rain-streaked window of a NYC tenement apartment at night. Through the distorted glass: "
            "blurred neon signs across the street — pink, red, electric blue — refracted into dreamy bokeh shapes "
            "by the water. A single moth fluttering at the glass from outside. Tungsten light glow from inside reflects "
            "faintly on the wet pane. Mood: melancholy, isolation, watching the world from inside. "
            "Composition: pure abstract atmosphere. No people."
        ),
    },
    {
        "filename": "broken_neon.png",
        "subject": (
            "Low-angle nighttime shot of a flickering, half-broken neon sign in a narrow Little Italy alley. "
            "The sign reads partial illegible italian-style script in pink and white tubes — some letters dead, "
            "buzzing. Sparks occasionally crackle. Rainwater puddles below reflect the pulsing light. "
            "Brick walls on either side, fire escape ladders descending into shadow. A black cat in the distance. "
            "Mood: forgotten, decaying glamour, hidden corners of the city. Period: 1994. No people."
        ),
    },
    {
        "filename": "milk_doorstep.png",
        "subject": (
            "Overhead close-up looking straight down: two glass milk bottles with paper caps left on the "
            "tiled doorstep of a 1990s apartment door (apartment number 202 partially visible on the door above). "
            "Condensation on the glass. A folded morning newspaper beside them, slightly wet. "
            "The brass kick-plate at the bottom of the door is scuffed. Warm hallway light from a wall sconce "
            "spills onto the tile. Mood: the rituals of an ordinary morning, before everything changes. "
            "No people. Symbolic, quiet, devastating in retrospect."
        ),
    },
]

def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def generate_one(item, idx, total):
    prompt = BASE + " Subject: " + item["subject"] + NEG
    out_path = OUTPUT_DIR / item["filename"]
    if out_path.exists():
        log(f"[{idx}/{total}] SKIP (exists): {item['filename']}"); return True

    log(f"[{idx}/{total}] Generating: {item['filename']}")
    payload = json.dumps({
        "model": MODEL, "prompt": prompt, "n": 1,
        "size": SIZE, "quality": QUALITY,
    }).encode("utf-8")

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
        b64 = data["data"][0]["b64_json"]
        png = base64.b64decode(b64)
        out_path.write_bytes(png)
        elapsed = time.time() - start
        log(f"[{idx}/{total}] OK ({elapsed:.1f}s, {len(png)//1024}KB): {item['filename']}")
        return True
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        log(f"[{idx}/{total}] HTTP {e.code}: {body[:300]}")
        return False
    except Exception as e:
        log(f"[{idx}/{total}] ERROR: {type(e).__name__}: {e}")
        return False

def main():
    log(f"=== Round 2: {len(IMAGES)} images ({QUALITY}, {SIZE}) ===")
    ok = fail = 0
    for i, item in enumerate(IMAGES, 1):
        if generate_one(item, i, len(IMAGES)): ok += 1
        else: fail += 1
        if i < len(IMAGES): time.sleep(2)
    log(f"=== Done. ok={ok}, fail={fail} ===")

if __name__ == "__main__":
    main()
