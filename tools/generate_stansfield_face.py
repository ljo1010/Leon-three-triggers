"""Regenerate stansfield_face.png — original Stansfield archetype, film-mood intensity (NOT a real actor).
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_stansfield_face.py
"""
import os, sys, json, base64, time, urllib.request, urllib.error
from pathlib import Path
API_KEY=os.environ.get("OPENAI_API_KEY")
if not API_KEY: print("ERROR"); sys.exit(1)
OUT=Path(__file__).parent.parent/"images"/"stansfield_face.png"
BASE=("Tight cinematic close-up character portrait, film still from a 1994 neo-noir thriller. 35mm film "
      "grain, harsh low-key side lighting, deep shadow, vignetting. Sickly warm green-amber noir color "
      "grade. No modern elements. No text, no watermarks. ")
NEG=(" Absolutely no: weapons, guns, firearms, blood, gore, violence, text, logos, watermarks, smartphones, "
     "modern vehicles, digital screens, cartoon, anime, 3D render, glossy CGI, plastic skin, oversaturation, "
     "HDR, children, minors. Do NOT depict any real or recognizable celebrity or actor; original fictional face only.")
SUBJECT=("An original fictional corrupt official in his early forties: a gaunt, pale, sweat-sheened face, "
         "damp disheveled dark hair falling over the brow, day-old stubble, and wild glassy heavy-lidded "
         "eyes with a cold drugged stare fixed straight into the camera. He wears a rumpled dark 1990s suit "
         "with a loosened tie. Harsh raking side light carves deep shadows across his face; beads of sweat "
         "catch the light. Barely-contained manic intensity beneath an unnervingly calm surface. "
         "Documentary realism, grainy, oppressive.")
prompt=BASE+" Subject: "+SUBJECT+NEG
payload=json.dumps({"model":"gpt-image-1","prompt":prompt,"n":1,"size":"1536x1024","quality":"high"}).encode()
for a in range(1,4):
    req=urllib.request.Request("https://api.openai.com/v1/images/generations",data=payload,
        headers={"Authorization":f"Bearer {API_KEY}","Content-Type":"application/json"},method="POST")
    s=time.time()
    try:
        with urllib.request.urlopen(req,timeout=300) as r: d=json.loads(r.read().decode())
        OUT.write_bytes(base64.b64decode(d["data"][0]["b64_json"])); print(f"OK ({time.time()-s:.1f}s)"); break
    except urllib.error.HTTPError as e:
        print(f"a{a} HTTP {e.code}: {e.read().decode('utf-8','replace')[:220]}")
        if e.code in (500,502,503,520) and a<3: time.sleep(5); continue
        break
    except Exception as e:
        print(f"a{a} ERR {e}")
        if a<3: time.sleep(5); continue
        break
