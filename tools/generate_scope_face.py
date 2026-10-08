"""scope_face.png — scope reticle centered on an unaware person (park target practice). May be blocked.
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_scope_face.py
"""
import os, sys, json, base64, time, urllib.request, urllib.error
from pathlib import Path
API_KEY=os.environ.get("OPENAI_API_KEY")
if not API_KEY: print("ERROR"); sys.exit(1)
OUT=Path(__file__).parent.parent/"images"/"scope_face.png"
BASE=("Cinematic film still from a 1994 character drama. 35mm film grain, telephoto compression, shallow "
      "depth of field, heavy vignetting. Warm natural daylight. No modern elements. No text, no watermarks. ")
NEG=(" Absolutely no: visible firearm, gun, rifle barrel, hands, blood, gore, wound, injury, violence, fear, "
     "crying, distress, logos, watermarks, smartphones, modern vehicles, cartoon, anime, 3D render, glossy "
     "CGI, oversaturation, HDR, children, minors.")
SUBJECT=("Point-of-view looking through a rifle scope: the frame masked by a large black circular optic "
         "vignette with thin faint crosshair reticle lines crossing the centre. Inside the bright circle, "
         "seen at a distance with telephoto compression, an unaware adult man calmly jogging through a "
         "sunny green park, his head loosely near the centre of the crosshair. Candid, calm, daytime, an "
         "ordinary moment observed from far away during target practice. No weapon in frame, no blood, "
         "no fear. Grainy, photographic, atmospheric.")
prompt=BASE+" Subject: "+SUBJECT+NEG
payload=json.dumps({"model":"gpt-image-1","prompt":prompt,"n":1,"size":"1536x1024","quality":"high"}).encode()
req=urllib.request.Request("https://api.openai.com/v1/images/generations",data=payload,
    headers={"Authorization":f"Bearer {API_KEY}","Content-Type":"application/json"},method="POST")
s=time.time()
try:
    with urllib.request.urlopen(req,timeout=300) as r: d=json.loads(r.read().decode())
    OUT.write_bytes(base64.b64decode(d["data"][0]["b64_json"])); print(f"OK ({time.time()-s:.1f}s)")
except urllib.error.HTTPError as e:
    print(f"HTTP {e.code}: {e.read().decode('utf-8','replace')[:400]}")
except Exception as e:
    print(f"ERR {e}")
