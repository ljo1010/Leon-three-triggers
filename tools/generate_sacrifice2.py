"""3 images for the sacrifice death climax: stansfield_looms, grenade_pin, stansfield_fear.
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_sacrifice2.py
"""
import os, sys, json, base64, time, urllib.request, urllib.error
from pathlib import Path
API_KEY=os.environ.get("OPENAI_API_KEY")
if not API_KEY: print("ERROR"); sys.exit(1)
OUTPUT_DIR=Path(__file__).parent.parent/"images"
LOG=OUTPUT_DIR/"_sac2.log"
BASE=("Film still from a 1994 neo-noir thriller. 35mm film grain, harsh low-key chiaroscuro, smoke haze, "
      "vignetting. Warm-cold dawn light bleeding through. No modern elements. No text, no watermarks. ")
NEG=(" Absolutely no: blood, gore, wounds, text, logos, watermarks, smartphones, modern vehicles, digital "
     "screens, cartoon, anime, 3D render, glossy CGI, plastic skin, oversaturation, HDR, children, minors. "
     "Do NOT depict any real or recognizable actor; original fictional faces only.")
STANS=("a gaunt sweat-sheened corrupt official in his forties in a rumpled dark 1990s suit and loosened tie, "
       "glassy heavy-lidded eyes, ")
IMAGES=[
 {"filename":"stansfield_looms.png","subject":(
   "In a smoke-filled building lobby at dawn, pale light flooding from a doorway behind. " + STANS +
   "stands looming over a man in a long dark coat and black knit beanie who has just dropped to his knees, "
   "back to the camera, head bowed. The standing official looks down at him with cold, drugged triumph. "
   "Backlit silhouettes, deep shadow, no blood, no visible weapon. Tense, final.")},
 {"filename":"grenade_pin.png","subject":(
   "Extreme close-up in dim smoky light: a wounded man's trembling hand presses a small dull metal ring "
   "into the open palm of another man's hand, forcing the fingers to close around it. Tense, intimate, "
   "ominous. Shallow depth of field, grain. Only the two hands and the small metal ring, nothing else.")},
 {"filename":"stansfield_fear.png","subject":(
   "Extreme tight close-up of the face of " + STANS + "as his glassy drugged calm cracks all at once into "
   "wide-eyed dawning terror — pupils sharpening, sweat beading, mouth parting. Harsh side light, deep "
   "shadow, smoke. Raw, sudden fear. No blood.")},
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
