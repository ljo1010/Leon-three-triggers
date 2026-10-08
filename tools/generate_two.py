"""Round 4: 2 specific shots for Leon_01_Hit."""
import os, sys, json, base64, time
import urllib.request, urllib.error
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY: print("ERROR"); sys.exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "images"
LOG_FILE = OUTPUT_DIR / "_two.log"

BASE = (
    "Film still from a 1994 neo-noir thriller set in Little Italy, New York City. "
    "Shot on 35mm film with visible grain, anamorphic lens flare, deep shadows, "
    "low-key chiaroscuro lighting. Cinematic letterbox composition, vignetting. "
    "Color graded with desaturated warm tones, crushed blacks. "
    "Reference: cinematography of Luc Besson's 1994 thriller by Thierry Arbogast. "
    "Practical lighting only. No modern elements. No text, no captions, no watermarks. "
    "Color palette: warm cream, beige, dusty olive. "
)
NEG = (
    " Absolutely no: text overlays, logos, watermarks, signatures, smartphones, "
    "modern vehicles, digital screens, cartoon, anime, 3D render, CGI, "
    "oversaturation, HDR, blood, gore, bodies, corpses, visible victims, faces of victims."
)

IMAGES = [
    {
        "filename": "leon_wristwatch.png",
        "subject": (
            "Extreme macro close-up of a vintage 1990s analog wristwatch on a man's wrist, viewed from above. "
            "The watch face is a classic Casio or Seiko diver-style, with a black dial, glowing tritium hands, "
            "and a unidirectional bezel. The second hand is visible at roughly the 12-second mark. "
            "The wrist wears a faded leather strap. A calloused index finger is just visible at the edge of frame. "
            "Background: dark, slightly out of focus — the textured metal interior of a ventilation duct. "
            "Single sliver of warm amber light cuts diagonally across the dial from a vent grille off-screen. "
            "Mood: held breath, count-down, the second before action. Shallow depth of field on the dial."
        ),
    },
    {
        "filename": "leon_smoke_clearing.png",
        "subject": (
            "Wide cinematic interior shot of a 1990s NYC luxury hotel suite, 14th floor, viewed from a high angle "
            "looking down (suggesting a vantage point from above the ceiling). "
            "Lingering gun smoke and dust particles hang and slowly dissipate in the air, drifting through "
            "diagonal shafts of amber tungsten lamp light. Overturned brass floor lamp on the carpet. "
            "Heavy crimson curtains slightly swaying. A fallen crystal glass on a coffee table, "
            "ice cubes melting on the wooden surface. Cigar still smoldering in an ashtray. "
            "An empty wingback chair pushed askew. The room is utterly silent. "
            "No people, no bodies, no victims visible at all — completely empty room aftermath. "
            "Mood: stillness after violence, smoke as breath of a room. "
            "Anamorphic widescreen composition. Period: 1994. Desaturated warm tones."
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
        log(f"[{idx}/{total}] OK ({time.time()-start:.1f}s, {len(png)//1024}KB): {item['filename']}")
        return True
    except urllib.error.HTTPError as e:
        log(f"[{idx}/{total}] HTTP {e.code}: {e.read().decode('utf-8', errors='replace')[:300]}")
        return False
    except Exception as e:
        log(f"[{idx}/{total}] ERROR: {type(e).__name__}: {e}")
        return False

def main():
    log(f"=== Two-shot batch ===")
    for i, it in enumerate(IMAGES, 1):
        gen(it, i, len(IMAGES))
        if i < len(IMAGES): time.sleep(2)
    log("=== Done ===")

if __name__ == "__main__": main()
