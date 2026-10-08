"""
Round 2 retry: 4 images with tone-downed prompts.
"""
import os, sys, json, base64, time
import urllib.request, urllib.error
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    print("ERROR: OPENAI_API_KEY env var not set"); sys.exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "images"
LOG_FILE = OUTPUT_DIR / "_retry2.log"

QUALITY = "high"
SIZE = "1536x1024"
MODEL = "gpt-image-1"

BASE = (
    "Film still from a 1994 character drama set in Little Italy, New York City. "
    "Shot on 35mm film with subtle grain, soft natural light, gentle warm tones. "
    "Cinematic letterbox composition, period-accurate. "
    "Color graded with warm desaturated palette, soft highlights. "
    "Practical lighting only — sunlight, lamps, candlelight. "
    "No modern elements. No text, no captions, no watermarks. "
)
NEG = (
    " Absolutely no: text overlays, logos, watermarks, signatures, smartphones, "
    "modern vehicles (post-1994), digital screens, cartoon, anime, 3D render, "
    "glossy CGI, plastic skin, oversaturation, HDR look, smoking, cigarettes, "
    "weapons, violence, threatening figures, dark alleys."
)

IMAGES = [
    {
        # Original triggered: 4am alley + dark coat + lone figure → predator
        # New: morning, casual, just a man walking with groceries
        "filename": "leon_dawn_walk.png",
        "subject": (
            "Wide cinematic shot of an adult man in a simple beige sweater walking down "
            "a quiet sunlit Little Italy NYC street in the early morning. He is carrying a paper grocery bag "
            "with a milk carton visible at the top. Soft golden morning light through the buildings. "
            "Old brick tenements line the street, with hanging laundry on fire escapes. "
            "A few wooden produce crates outside an Italian grocery shop. A black cat sits on a stoop. "
            "Warm palette of cream, beige, terracotta. Mood: an ordinary peaceful morning. "
            "Period: 1994, but bright and gentle."
        ),
    },
    {
        # Original triggered: empty chair pulled out + clandestine meeting place
        # New: warm welcoming family restaurant, no narrative implication
        "filename": "italian_restaurant.png",
        "subject": (
            "Interior of a warm, welcoming Italian family restaurant in Little Italy NYC, 1994. "
            "Red checkered tablecloths neatly set with empty wine glasses and white napkins. "
            "Wine bottles in straw baskets on a wooden shelf. Framed black-and-white family photographs "
            "on the brick walls. A vintage chrome espresso machine gleams in the background. "
            "Strings of small warm bulb lights cross the ceiling. Bread baskets and olive oil bottles on tables. "
            "An open kitchen pass-through with soft golden light. Tomato vines in a basket. "
            "Mood: nostalgic, inviting, family-owned, before opening hours. "
            "Warm reds, deep greens, golden tones. No people."
        ),
    },
    {
        # Original triggered: smoking
        # New: coffee cup + steam, same contemplative mood
        "filename": "coffee_window.png",
        "subject": (
            "Close-up of a white ceramic coffee mug on a wooden windowsill, steam curling upward into a shaft "
            "of pale morning light from a window with iron security bars. The window overlooks a brick wall "
            "across the air shaft. Out of focus in the background: a folded newspaper, a small potted herb plant, "
            "a single brass key. The coffee surface shows a hint of cream swirl. "
            "Mood: morning solitude, the long quiet pause before the day begins. "
            "Warm cream and amber tones. Shallow depth of field on the steam. No people."
        ),
    },
    {
        # Original triggered: apt 202 + "before everything changes"
        # New: generic morning milk delivery, no dark subtext
        "filename": "milk_doorstep.png",
        "subject": (
            "Overhead close-up looking straight down at two glass milk bottles with classic paper caps left on "
            "an old tiled apartment doorstep. Soft condensation on the glass. A folded morning newspaper beside them. "
            "The wooden apartment door above is painted dark green with brass fittings. "
            "Warm hallway light from a wall sconce spills onto the patterned mosaic floor tiles. "
            "Mood: an ordinary, peaceful morning ritual in a 1990s NYC apartment building. "
            "Warm amber and cream tones. Period: 1994. No people. Pure object composition."
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

    log(f"[{idx}/{total}] Retrying: {item['filename']}")
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
        log(f"[{idx}/{total}] OK ({time.time()-start:.1f}s, {len(png)//1024}KB): {item['filename']}")
        return True
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        log(f"[{idx}/{total}] HTTP {e.code}: {body[:300]}")
        return False
    except Exception as e:
        log(f"[{idx}/{total}] ERROR: {type(e).__name__}: {e}")
        return False

def main():
    log(f"=== Retry 2 batch: {len(IMAGES)} images ===")
    ok = fail = 0
    for i, item in enumerate(IMAGES, 1):
        if generate_one(item, i, len(IMAGES)): ok += 1
        else: fail += 1
        if i < len(IMAGES): time.sleep(2)
    log(f"=== Done. ok={ok}, fail={fail} ===")

if __name__ == "__main__":
    main()
