"""
Round 3: Mathilda direct portraits as young adult woman.
Narrative role: protected/protector dynamic — age is flexible per user's call.
"""
import os, sys, json, base64, time
import urllib.request, urllib.error
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    print("ERROR: OPENAI_API_KEY env var not set"); sys.exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "images"
LOG_FILE = OUTPUT_DIR / "_mathilda.log"

QUALITY = "high"
SIZE = "1536x1024"
MODEL = "gpt-image-1"

# Use the gentler character-drama BASE that worked for round-2 retries
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
    "modern vehicles (post-1994), digital screens, cartoon style, anime style, 3D render, "
    "glossy CGI, plastic skin, oversaturation, HDR look, minors, children, "
    "sexual content, suggestive poses, romantic implication between characters."
)

# Reusable Mathilda character description (consistent across shots)
MATHILDA_DESC = (
    "A young adult woman in her early twenties with a chin-length dark bob haircut "
    "and serious, quiet eyes. Slim build. Wearing a simple oversized dark sweater "
    "and worn jeans. No makeup. A pensive, watchful expression. "
    "Mossy green and dusty rose color palette in her clothing and lighting. "
)

IMAGES = [
    {
        "filename": "mathilda_portrait.png",
        "subject": (
            MATHILDA_DESC +
            "Tight portrait shot, three-quarter angle, looking off-camera to the side toward a window. "
            "She is sitting on the edge of a worn velvet armchair in a dim 1990s NYC tenement apartment. "
            "Soft window light falls on half of her face, the other half in shadow. "
            "Mood: introspective, guarded, carrying recent grief. No movement, no action. "
            "Shallow depth of field. Pure character study composition."
        ),
    },
    {
        "filename": "mathilda_in_apartment.png",
        "subject": (
            MATHILDA_DESC +
            "Wide shot of her standing alone at a tall window in a small sparse 1990s apartment, looking out at the city. "
            "Her back is mostly to camera, only her profile visible. "
            "On the windowsill beside her: a small potted houseplant. "
            "Morning light streams in around her silhouette. The apartment behind her is bare — "
            "a single wooden chair, a folded blanket, a milk carton on a small table. "
            "Mood: she is a guest in someone else's quiet life, taking it in."
        ),
    },
    {
        "filename": "mathilda_with_leon.png",
        "subject": (
            "Two characters in a dim 1990s NYC tenement apartment kitchen at night, lit only by a single overhead "
            "pendant lamp casting a warm cone of light onto a wooden table. "
            "On the LEFT: an adult man in his late thirties, tall, wearing a simple beige sweater and a leather harness, "
            "round dark glasses, dark short hair. His posture is protective but professional, not affectionate — "
            "he stands slightly in front, watchful, body angled toward the apartment door. "
            "On the RIGHT: a young adult woman in her early twenties with a chin-length dark bob, serious eyes, "
            "wearing an oversized dark sweater. She stands behind him, smaller, looking out toward the door as well. "
            "There is professional, careful distance between them — like a bodyguard and a witness, not family. "
            "Mood: silent partnership, mutual protection, the weight of shared danger. "
            "Composition: both in three-quarter view, the lamp light unifies them. No touching."
        ),
    },
    {
        "filename": "mathilda_training.png",
        "subject": (
            MATHILDA_DESC +
            "She is at an indoor practice shooting range during daytime, wearing professional ear protection muffs "
            "and clear safety glasses. She holds a small target pistol with both hands in a careful, instructed grip, "
            "barrel pointed downrange at a paper target visible in the deep background. "
            "An adult male instructor (out of focus, only his hands visible) gently corrects her grip from behind. "
            "Soft overhead fluorescent light. Clean, professional, training-context atmosphere. "
            "Mood: focused concentration, learning a skill. NOT threatening. NOT in a home setting. "
            "This is a regulated, safe environment."
        ),
    },
    {
        "filename": "mathilda_mourning.png",
        "subject": (
            MATHILDA_DESC +
            "Close-up portrait shot. She is sitting alone on a flight of dim concrete stairs, knees drawn up, "
            "arms wrapped around her shins. Her cheek rests on her knee. Eyes open but unfocused, "
            "a single tear track visible. She is not sobbing — just hollowed out, quiet grief. "
            "Single overhead fluorescent light from above casts a soft glow. "
            "Mood: the long pause after loss. No other people in frame. "
            "Composition: she occupies the lower-right third, vast empty stairwell above her. "
            "Shallow depth of field on her face."
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
    log(f"=== Mathilda batch: {len(IMAGES)} images ===")
    ok = fail = 0
    for i, item in enumerate(IMAGES, 1):
        if generate_one(item, i, len(IMAGES)): ok += 1
        else: fail += 1
        if i < len(IMAGES): time.sleep(2)
    log(f"=== Done. ok={ok}, fail={fail} ===")

if __name__ == "__main__":
    main()
