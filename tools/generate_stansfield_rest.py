"""Regenerate the other 3 Stansfield images to match the intense film-mood portrait. Overwrites.
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_stansfield_rest.py
"""
import os, sys, json, base64, time, urllib.request, urllib.error
from pathlib import Path
API_KEY=os.environ.get("OPENAI_API_KEY")
if not API_KEY: print("ERROR"); sys.exit(1)
OUTPUT_DIR=Path(__file__).parent.parent/"images"
LOG=OUTPUT_DIR/"_stans.log"
BASE=("Film still from a 1994 neo-noir thriller. 35mm film grain, harsh low-key chiaroscuro, deep shadow, "
      "vignetting. Sickly warm green-amber noir color grade. No modern elements. No text, no watermarks. ")
CHAR=("an original fictional corrupt official in his early forties: gaunt, pale, sweat-sheened face, damp "
      "disheveled dark hair, day-old stubble, wild glassy heavy-lidded drugged eyes, a rumpled dark 1990s "
      "suit with a loosened tie. ")
NEG=(" Absolutely no: weapons, guns, firearms, blood, gore, violence, text, logos, watermarks, smartphones, "
     "modern vehicles, digital screens, cartoon, anime, 3D render, glossy CGI, plastic skin, oversaturation, "
     "HDR, children, minors. Do NOT depict any real or recognizable celebrity or actor; original fictional face only.")
IMAGES=[
 {"filename":"stansfield_desk.png","subject":(
   "He slumps at a cluttered government office desk at night, head tilted back, eyes half-closed, lost in "
   "music through a single earphone. Two small white pills and a glass of water sit on the desk beside a "
   "case file. Detached, drugged, dreamy, unsettling calm. Cold fluorescent light mixed with a warm desk "
   "lamp. He is " + CHAR)},
 {"filename":"stansfield_tony.png","subject":(
   "Inside a dim empty Little Italy restaurant before opening. He stands calmly and coldly beside a "
   "checkered-cloth table, looking down at a tense seated older heavyset Italian-American restaurateur "
   "whose hands lie flat on a folded newspaper. A quiet, unhurried, unsettling confrontation. Wine bottles "
   "and warm wall lamps behind. The standing man is " + CHAR)},
 {"filename":"clipping_stansfield.png","subject":(
   "Extreme close-up of a torn newspaper halftone clipping lying on a worn wooden floor under a warm lamp: "
   "a grainy black-and-white newspaper photograph of " + CHAR + " visible halftone print dots, yellowed "
   "torn newsprint with blurred unreadable columns of text around the photo. The target. Ominous, intimate, "
   "shallow depth of field. No people in the room, only the clipping.")},
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
