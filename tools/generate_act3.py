"""Generate 8 dedicated ACT 3 images. Policy-safe framing.
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_act3.py
"""
import os, sys, json, base64, time
import urllib.request, urllib.error
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    print("ERROR: set OPENAI_API_KEY"); sys.exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "images"
LOG_FILE = OUTPUT_DIR / "_act3.log"

BASE = (
    "Film still from a 1994 neo-noir character drama set in New York City. "
    "Shot on 35mm film with subtle grain, low-key chiaroscuro lighting. "
    "Cinematic letterbox composition, vignetting. "
    "Color graded with warm desaturated cream, beige and dusty olive tones. "
    "Moody but readable. Practical lighting only — tungsten lamps, window light, flashlight beams. "
    "No modern elements. No text, no captions, no watermarks. "
)
NEG = (
    " Absolutely no: fedora, brimmed hat, trench coat with belt, text overlays, logos, watermarks, "
    "signatures, smartphones, modern vehicles, digital screens, cartoon, anime, 3D render, glossy CGI, "
    "plastic skin, oversaturation, HDR, weapons, guns, firearms, blood, gore, violence, "
    "menacing expression, children, minors."
)
# Leon's iconic look for silhouettes
LEON = ("a solitary man in a long dark wool overcoat, small round dark sunglasses, and a snug BLACK KNIT "
        "WOOL BEANIE (rounded top, no brim), ")

IMAGES = [
    {
        "filename": "leon_pursuit.png",
        "subject": (
            "From behind, the silhouette of " + LEON +
            "standing in the doorway of a dim 1990s tenement apartment at night, about to step into a "
            "warmly lit hallway. Resolute and still, the set of his shoulders carrying grim purpose. "
            "Warm light ahead, deep shadow around him. Iconic and determined. No weapons."
        ),
    },
    {
        "filename": "stansfield_desk.png",
        "subject": (
            "A disheveled man in his forties in a loosened tie and rolled-up sleeves slumps at a cluttered "
            "government office desk at night, eyes half-closed, head tilted as if lost in music through a "
            "single earphone. Two small white pills rest on the desk beside a glass of water and a case "
            "file. Detached, drugged, dreamy calm — NOT menacing, simply absent, far away in the music. "
            "Cold fluorescent light mixed with a warm desk lamp. Unsettling quiet. No weapons."
        ),
    },
    {
        "filename": "siege_corridor.png",
        "subject": (
            "Point of view from inside a dark apartment looking toward a doorway flooded with harsh white "
            "flashlight beams and the crowded silhouettes of many armored tactical figures in the smoky "
            "hallway beyond. Dust and haze in the shafts of light. Overwhelming tension, the feeling of "
            "being surrounded. Cold blue-white light against warm interior shadow. "
            "No visible firearms, no blood."
        ),
    },
    {
        "filename": "vent_escape.png",
        "subject": (
            "A young woman in her early twenties with short dark bobbed hair climbs into a rectangular wall "
            "air-vent opening in a dim, smoke-hazed apartment, one hand gripping the metal edge, looking "
            "back over her shoulder. Dust motes drift in a shaft of light. Fear and trust mixed on her "
            "face. Cramped, intimate, urgent. Warm-grey desaturated palette. No weapons."
        ),
    },
    {
        "filename": "end_light.png",
        "subject": (
            "A lone backlit silhouette of " + LEON +
            "standing at the end of a smoke-filled corridor as blinding warm white light floods toward the "
            "camera and swallows his outline. Dust and haze drift through the light. A sense of finality, "
            "release and peace rather than violence. Strong rim light, deep shadow. No weapons, no blood."
        ),
    },
    {
        "filename": "end_milk_plant.png",
        "subject": (
            "Still life on a sunlit windowsill in a peaceful apartment: two glasses of milk catching warm "
            "morning light, and beside them a healthy green potted plant that has clearly taken root and "
            "grown. Soft lace curtain, gentle hopeful atmosphere. Documentary realism, shallow depth of "
            "field. Warm cream and amber palette. No people."
        ),
    },
    {
        "filename": "end_revenge.png",
        "subject": (
            "The backlit silhouette of a young woman in her early twenties, short dark bobbed hair, "
            "standing alone and seen from behind in a doorway filled with thin drifting smoke, her posture "
            "cold and still, a long shadow stretching toward the camera. A single warm light source behind "
            "her. A sense of lost innocence hardened to stone. Ambiguous and quiet. No blood, no weapons. "
            "Desaturated cool palette with a sliver of warm light."
        ),
    },
    {
        "filename": "school_planting.png",
        "subject": (
            "A young woman in her early twenties with short dark bobbed hair kneels on a wide sunlit green "
            "lawn on a gentle hill, gently pressing the soil around a small green potted plant she has just "
            "planted into the earth. Soft warm afternoon light, a peaceful old boarding-school building "
            "blurred in the distance. Hope, quiet grief, new roots taking hold. Documentary realism, "
            "shallow depth of field. Warm natural palette."
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
    for attempt in range(1, 4):
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
