"""5 images for the expanded Stansfield-visits-Tony scene. Policy-safe.
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_tonyscene.py
"""
import os, sys, json, base64, time, urllib.request, urllib.error
from pathlib import Path
API_KEY=os.environ.get("OPENAI_API_KEY")
if not API_KEY: print("ERROR"); sys.exit(1)
OUTPUT_DIR=Path(__file__).parent.parent/"images"
LOG=OUTPUT_DIR/"_tony.log"
BASE=("Film still from a 1994 neo-noir character drama set in Little Italy, New York City. 35mm film grain, "
      "low-key warm tungsten lighting, cinematic, vignetting. Warm desaturated cream, amber and olive tones. "
      "Practical lighting only. No modern elements. No text, no watermarks. ")
NEG=(" Absolutely no: weapons, guns, firearms, blood, violence, logos, watermarks, smartphones, modern "
     "vehicles, digital screens, cartoon, anime, 3D render, glossy CGI, plastic skin, oversaturation, HDR, "
     "minors, children.")
IMAGES=[
 {"filename":"tony_restaurant_night.png","subject":(
   "Interior of a small, empty Little Italy family restaurant late at night, lights low: checkered "
   "tablecloths, chairs turned upside-down on some tables, shelves of wine bottles, warm wall lamps, a "
   "long shadow across the floor. Deserted, hushed, ominous calm. No people. Cinematic wide shot.")},
 {"filename":"prop_family_photo.png","subject":(
   "Cinematic still-life close-up: a worn, slightly faded old color family snapshot lying on a red-checked "
   "restaurant tablecloth under a warm lamp. The smiling figures in the photograph are soft, blurred and "
   "indistinct. A creased, much-loved keepsake, quietly menacing in this context. Shallow depth of field. "
   "No clearly visible faces, no people in the room — only the photo on the cloth.")},
 {"filename":"tony_hands_newspaper.png","subject":(
   "Close-up of an older heavyset man's thick, weathered hands resting flat and tense on a folded "
   "newspaper on a red-checked tablecloth, a glass of red wine beside them, warm lamplight. Quiet dread, "
   "stillness. Only the hands, no face. Shallow depth of field.")},
 {"filename":"tony_defeated.png","subject":(
   "Tight low-key portrait of a tired older Italian-American restaurateur in his early sixties, silver hair "
   "combed back, heavy lined face, reading glasses, sitting at his table with his eyes closed in weary "
   "resignation, head slightly bowed — a proud old man who has just lost something. Warm lamp light on one "
   "side, deep shadow. Documentary realism, melancholy.")},
 {"filename":"stansfield_radio.png","subject":(
   "Close-up of a lean man's hand raising a small black handheld two-way radio toward his mouth in a dim "
   "restaurant, warm lamplight catching the device, the man's rumpled suit sleeve and loosened tie blurred "
   "behind. Cold, decisive. Just the hand and the radio, no weapon. Shallow depth of field.")},
]
def log(m):
    line=f"[{time.strftime('%H:%M:%S')}] {m}"; print(line,flush=True)
    with open(LOG,"a",encoding="utf-8") as f: f.write(line+"\n")
def gen(it,i,n):
    prompt=BASE+" Subject: "+it["subject"]+NEG
    out=OUTPUT_DIR/it["filename"]; log(f"[{i}/{n}] {it['filename']}")
    payload=json.dumps({"model":"gpt-image-1","prompt":prompt,"n":1,"size":"1536x1024","quality":"high"}).encode()
    for a in range(1,4):
        req=urllib.request.Request("https://api.openai.com/v1/images/generations",data=payload,
            headers={"Authorization":f"Bearer {API_KEY}","Content-Type":"application/json"},method="POST")
        s=time.time()
        try:
            with urllib.request.urlopen(req,timeout=300) as r: d=json.loads(r.read().decode())
            out.write_bytes(base64.b64decode(d["data"][0]["b64_json"])); log(f"[{i}/{n}] OK ({time.time()-s:.1f}s)"); return True
        except urllib.error.HTTPError as e:
            log(f"[{i}/{n}] a{a} HTTP {e.code}: {e.read().decode('utf-8','replace')[:200]}")
            if e.code in (500,502,503,520) and a<3: time.sleep(5); continue
            return False
        except Exception as e:
            log(f"[{i}/{n}] a{a} ERR {e}")
            if a<3: time.sleep(5); continue
            return False
ok=0
for i,it in enumerate(IMAGES,1):
    if gen(it,i,len(IMAGES)): ok+=1
    time.sleep(1)
log(f"=== Done {ok}/{len(IMAGES)} ===")
