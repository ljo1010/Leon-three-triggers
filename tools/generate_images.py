"""
LEON: Three Triggers — Batch Image Generator
Generates 12 cinematic images via OpenAI gpt-image-1 API.

Usage:
    export OPENAI_API_KEY="sk-..."
    python tools/generate_images.py
"""
import os
import sys
import json
import base64
import time
import urllib.request
import urllib.error
from pathlib import Path

# ===== CONFIG =====
API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    print("ERROR: OPENAI_API_KEY env var not set")
    sys.exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "images"
OUTPUT_DIR.mkdir(exist_ok=True)
LOG_FILE = OUTPUT_DIR / "_generation.log"

QUALITY = "high"
SIZE = "1536x1024"
MODEL = "gpt-image-1"

# ===== TONE PRESETS =====
BASE = (
    "Film still from a 1994 neo-noir thriller set in Little Italy, New York City. "
    "Shot on 35mm film with visible grain, anamorphic lens flare, deep shadows, "
    "low-key chiaroscuro lighting. Cinematic letterbox composition, vignetting. "
    "Color graded with desaturated warm tones, crushed blacks, slightly faded highlights. "
    "Reference: cinematography of Luc Besson's 'Léon: The Professional' (1994) by Thierry Arbogast. "
    "Practical lighting only — tungsten bulbs, neon signs, window light. "
    "No modern elements. No text, no captions, no watermarks. "
)

POV = {
    "leon": (
        "Color palette dominated by warm cream, beige, dusty olive. "
        "Quiet, contemplative mood. Composition emphasizes solitude — isolated figures, "
        "empty space, single light source. A sense of stillness before violence. "
    ),
    "mathilda": (
        "Color palette dominated by mossy green, dusty rose, faded yellows. "
        "Subjective child's-eye-level POV when possible. "
        "Mood: vulnerable but defiant, watchful. Slight handheld feel. "
    ),
    "stansfield": (
        "Color palette dominated by sickly purple, fluorescent magenta, cold cyan shadows. "
        "Disorienting angles, dutch tilt, harsh shadow patterns. "
        "Mood: euphoric menace, hallucinatory edge. Slightly overexposed highlights. "
    ),
    "none": "",
}

SCENE = {
    "environment": (
        "Wide environmental shot. No central character; the space itself is the subject. "
        "Architectural details — peeling wallpaper, exposed pipes, single window light. "
    ),
    "portrait": (
        "Tight character portrait, shallow depth of field, face partially in shadow. "
        "Subject is NOT looking directly at camera. Three-quarter angle. Focus on hands or eyes. "
    ),
    "object": (
        "Macro close-up of a single object on a flat surface. Shallow depth of field. "
        "The object tells a story — domestic but loaded with meaning. "
        "Soft directional light from one side. "
    ),
    "action": (
        "Mid-action moment frozen, motion blur on extremities only. "
        "Tension in body language. Cropped tightly. No clear resolution visible. "
    ),
    "cinematic": (
        "Wide cinematic establishing shot, 2.39:1 aspect ratio feel. "
        "Architecture and city as character. Negative space. "
        "A single small figure dwarfed by environment. "
    ),
}

NEGATIVE = (
    " Absolutely no: text overlays, logos, watermarks, signatures, modern smartphones, "
    "modern cars (post-1994), digital screens, cartoon style, anime style, 3D render look, "
    "glossy CGI, plastic skin, oversaturation, HDR look."
)

# ===== IMAGE LIST =====
IMAGES = [
    {
        "filename": "title.png",
        "pov": "none",
        "scene": "cinematic",
        "subject": (
            "A title-card style cinematic poster shot. A lone silhouette of a man in a long dark coat "
            "standing at the end of a long, dim NYC apartment hallway at dawn. Single bare bulb flickering. "
            "Empty milk carton on the floor. Wide aspect, very tall vertical lines, deep negative space "
            "above for a title to be added later (but do not render any text)."
        ),
    },
    {
        "filename": "leon_apartment.png",
        "pov": "leon",
        "scene": "environment",
        "subject": (
            "A small, sparse 1990s NYC apartment at 4am. A single wooden chair beside a tall window. "
            "A potted plant (a single houseplant in a clay pot) on the windowsill. "
            "A half-empty milk carton on a small table. No bed visible — just blankets on a chair. "
            "Cool dawn light through gauzy curtains. Tungsten lamp casts a warm pool of light. "
            "Bare walls, no decoration. The room feels lived-in but emotionally empty."
        ),
    },
    {
        "filename": "leon_door_choice.png",
        "pov": "leon",
        "scene": "object",
        "subject": (
            "Extreme close-up: a man's calloused hand resting on a brass apartment doorknob, frozen mid-motion. "
            "His other hand, slightly out of focus in foreground, holds a matte-black Beretta 92FS pistol "
            "pointed downward. Old peeling paint on the door. A sliver of yellow hallway light leaks "
            "through the gap below the door. Tense, undecided moment."
        ),
    },
    {
        "filename": "mathilda_hallway.png",
        "pov": "mathilda",
        "scene": "environment",
        "subject": (
            "A flickering fluorescent-lit apartment building hallway, 4th floor, 1994 NYC tenement. "
            "Worn green linoleum floor. A 12-year-old girl with a dark bob haircut and a slightly swollen eye "
            "sits on the stairwell landing, half-shadowed, clutching a small milk carton. "
            "Door of apartment 201 visible behind her. Distant POV, voyeuristic, from down the hall. "
            "Single flickering tube light overhead."
        ),
    },
    {
        "filename": "stansfield_face.png",
        "pov": "stansfield",
        "scene": "portrait",
        "subject": (
            "A close-up portrait of a corrupt DEA agent in his 40s, mid-hum, eyes half-closed in drug-fueled euphoria. "
            "Wearing a wrinkled tan suit and loose tie. Receding hairline, sweat on his temple. "
            "His mouth is slightly open as if humming Beethoven. "
            "Lit from below by sickly fluorescent hallway light. "
            "Slight dutch tilt. His face dominates the frame but his eyes are unfocused, drugged."
        ),
    },
    {
        "filename": "leon_hotel_hit.png",
        "pov": "leon",
        "scene": "action",
        "subject": (
            "POV shot from inside a metal ventilation duct on the 14th floor of an old NYC hotel. "
            "Looking down through a vent grille into a luxury hotel suite. Below: scattered chairs, "
            "a fallen wine glass, a thin trail of smoke from a recently fired weapon. "
            "Dim red exit-sign light reflects off the ducts. The shot is taken from above, almost top-down. "
            "Visible breath fog on the metal. No bodies visible — only aftermath."
        ),
    },
    {
        "filename": "leon_stairs_mathilda.png",
        "pov": "leon",
        "scene": "environment",
        "subject": (
            "A view through a narrow apartment door gap (the door of 202) into a tenement hallway. "
            "On the staircase landing across the hall: a 12-year-old girl with a bruised eye sits "
            "holding a milk carton, looking down at the floor. She doesn't know she's being watched. "
            "Strong vertical bars of the stair railing cast prison-like shadows across her face. "
            "Voyeuristic, restrained composition."
        ),
    },
    {
        "filename": "mathilda_hide.png",
        "pov": "mathilda",
        "scene": "object",
        "subject": (
            "Low-angle close-up: a fallen white milk carton on dirty concrete tenement-stairwell floor, "
            "white milk pooling and spreading across the floor. In the background, slightly out of focus, "
            "the legs of men in dark dress shoes and dark suit pants walking away. "
            "From the perspective of a child crouched behind a fire-escape staircase. "
            "Cold green-tinted fluorescent light, oppressive geometry of metal stair beams."
        ),
    },
    {
        "filename": "mathilda_knock.png",
        "pov": "mathilda",
        "scene": "environment",
        "subject": (
            "POV shot of a 12-year-old girl's perspective standing directly in front of an old wooden "
            "apartment door (number 202 visible). A thin warm yellow strip of light glows from under the door "
            "into the dim hallway. The girl's small hand (only fingers visible at bottom of frame) "
            "raised, hesitant, about to knock. The peephole stares back like an eye. "
            "Intimate, frightened intimacy with the door."
        ),
    },
    {
        "filename": "clue_milk.png",
        "pov": "none",
        "scene": "object",
        "subject": (
            "Extreme macro close-up of a vintage 1990s white paper milk carton standing on a scratched "
            "wooden table. Condensation droplets on the carton. Soft directional light from a window "
            "creates a single highlight. Shallow depth of field. The carton is plain, generic — "
            "no readable text or logo, just the shape and the iconic gable top. "
            "Symbolic, contemplative. Background completely dark."
        ),
    },
    {
        "filename": "clue_plant.png",
        "pov": "none",
        "scene": "object",
        "subject": (
            "Extreme macro close-up of a small houseplant — a single Aglaonema (Chinese evergreen) "
            "in a simple terracotta clay pot, on a wooden windowsill. Soft morning light from the side "
            "catches the dust on the broad green leaves. A few water droplets remain on a leaf. "
            "The plant has no roots in soil visible — feels portable, rootless. "
            "Background is dark, out-of-focus apartment interior."
        ),
    },
    {
        "filename": "clue_pistol.png",
        "pov": "none",
        "scene": "object",
        "subject": (
            "Extreme macro close-up of a matte-black Beretta 92FS pistol lying disassembled on a clean "
            "white cloth on a wooden table. Slide separate from frame, barrel beside it, magazine vertical. "
            "A small bottle of gun oil and a cleaning rod visible at edge. Single overhead lamp lights it "
            "like a surgeon's table. Cold, methodical, ritual. Tiny scratches on the slide show heavy use. "
            "No hands, no person — just the disassembled weapon."
        ),
    },
]

# ===== MAIN =====
def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def build_prompt(item):
    return BASE + POV[item["pov"]] + SCENE[item["scene"]] + " Subject: " + item["subject"] + NEGATIVE

def generate_one(item, idx, total):
    prompt = build_prompt(item)
    out_path = OUTPUT_DIR / item["filename"]
    if out_path.exists():
        log(f"[{idx}/{total}] SKIP (exists): {item['filename']}")
        return True

    log(f"[{idx}/{total}] Generating: {item['filename']} (pov={item['pov']}, scene={item['scene']})")

    payload = json.dumps({
        "model": MODEL,
        "prompt": prompt,
        "n": 1,
        "size": SIZE,
        "quality": QUALITY,
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.openai.com/v1/images/generations",
        data=payload,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
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
        err_body = e.read().decode("utf-8", errors="replace")
        log(f"[{idx}/{total}] HTTP {e.code}: {err_body[:300]}")
        return False
    except Exception as e:
        log(f"[{idx}/{total}] ERROR: {type(e).__name__}: {e}")
        return False

def main():
    log(f"=== Starting batch of {len(IMAGES)} images ({QUALITY}, {SIZE}) ===")
    ok = 0
    fail = 0
    for i, item in enumerate(IMAGES, 1):
        if generate_one(item, i, len(IMAGES)):
            ok += 1
        else:
            fail += 1
        # gentle throttle
        if i < len(IMAGES):
            time.sleep(2)
    log(f"=== Done. ok={ok}, fail={fail} ===")

if __name__ == "__main__":
    main()
