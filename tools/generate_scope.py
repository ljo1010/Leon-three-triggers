"""scope_view.png — POV through a rifle scope (surveillance/aim), policy-safe (no clear face, no gun).
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_scope.py
"""
import os, sys, json, base64, time, urllib.request, urllib.error
from pathlib import Path
API_KEY=os.environ.get("OPENAI_API_KEY")
if not API_KEY: print("ERROR"); sys.exit(1)
OUT=Path(__file__).parent.parent/"images"/"scope_view.png"
BASE=("Cinematic film still from a 1994 neo-noir character drama. 35mm film grain, telephoto compression, "
      "shallow depth of field, heavy vignetting. Warm desaturated dusk tones. No modern elements. "
      "No text, no captions, no watermarks. ")
NEG=(" Absolutely no: visible firearm, gun, rifle barrel, hands, clear human face, portrait, blood, gore, "
     "violence, logos, watermarks, smartphones, modern vehicles, cartoon, anime, 3D render, glossy CGI, "
     "oversaturation, HDR, children, minors.")
SUBJECT=("Point-of-view looking THROUGH a rifle scope: the frame is masked by a large black circular "
         "vignette (the optic), with faint thin crosshair reticle lines crossing the centre. Inside the "
         "bright circle, seen across a city at dusk through telephoto compression, a distant apartment "
         "building with one warm softly-lit window; in that far window, a small indistinct dark silhouette "
         "stands, barely recognizable. Tense, quiet surveillance from afar. Grainy, atmospheric. "
         "No weapon in frame, no clear face.")
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
