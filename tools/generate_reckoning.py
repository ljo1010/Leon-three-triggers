"""2 images for the 'shot the wrist' divergent branch: stansfield_wounded, end_reckoning.
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_reckoning.py
"""
import os, sys, json, base64, time, urllib.request, urllib.error
from pathlib import Path
API_KEY=os.environ.get("OPENAI_API_KEY")
if not API_KEY: print("ERROR"); sys.exit(1)
OUTPUT_DIR=Path(__file__).parent.parent/"images"
LOG=OUTPUT_DIR/"_reck.log"
BASE=("Film still from a 1994 neo-noir thriller. 35mm film grain, harsh low-key chiaroscuro, deep shadow, "
      "vignetting. Sickly warm green-amber noir grade. No modern elements. No text, no watermarks. ")
NEG=(" Absolutely no: blood, gore, wounds, injury detail, text, logos, watermarks, smartphones, modern "
     "vehicles, digital screens, cartoon, anime, 3D render, glossy CGI, plastic skin, oversaturation, HDR, "
     "children, minors. Do NOT depict any real or recognizable actor; original fictional faces only.")
LEON=("a lean weathered hitman in a long dark coat and a black knit beanie, ")
STANS=("a gaunt sweat-sheened corrupt official in his forties in a rumpled dark 1990s suit and loosened tie, "
       "with glassy heavy-lidded eyes, ")
IMAGES=[
 {"filename":"stansfield_wounded.png","subject":(
   "In a dim office corridor at night, " + STANS + "recoils and grips his own right wrist hard with his "
   "left hand, his face contorted in shocked rage and pain, staggering backward. Harsh side light, deep "
   "shadow. No blood, no weapon visible. Raw, intense, humiliated fury.")},
 {"filename":"end_reckoning.png","subject":(
   "A dark, smoke-filled tenement apartment. In the foreground, the tall still backlit silhouette of " +
   LEON + "standing over a defeated man slumped against the wall on the floor — " + STANS + "cradling a "
   "limp, ruined right hand against his chest and looking up in dread. A cold, quiet final reckoning. "
   "Strong rim light through smoke, deep shadow. No blood, no visible weapon.")},
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
