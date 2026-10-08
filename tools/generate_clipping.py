"""clipping_stansfield.png — newspaper clipping of Stansfield's face (the target). Prop close-up.
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_clipping.py
"""
import os, sys, json, base64, time, urllib.request, urllib.error
from pathlib import Path
API_KEY=os.environ.get("OPENAI_API_KEY")
if not API_KEY: print("ERROR"); sys.exit(1)
OUT=Path(__file__).parent.parent/"images"/"clipping_stansfield.png"
BASE=("Cinematic still-life from a 1994 neo-noir character drama. 35mm film grain, low-key warm tungsten "
      "lamplight, shallow depth of field, vignetting. Warm desaturated amber tones. No modern elements. "
      "No watermarks, no logos. ")
# allow newsprint texture, but no legible/meaningful words
NEG=(" Absolutely no: legible words, readable headlines, captions, watermarks, logos, smartphones, modern "
     "vehicles, digital screens, cartoon, anime, 3D render, glossy CGI, plastic skin, oversaturation, HDR, "
     "blood, violence, weapons, children, minors.")
SUBJECT=("Extreme close-up of a torn newspaper clipping lying on a worn wooden floor under a warm lamp: a "
         "grainy black-and-white halftone newspaper photograph of a gaunt man in his forties wearing a "
         "suit and tie, slicked-back hair, a tired hollow face and heavy-lidded glassy unfocused eyes — a "
         "cold, detached, drugged calm. Visible halftone print dots, slightly yellowed torn newsprint with "
         "blurred unreadable columns of text around the photo. The target. Intimate, ominous, "
         "shallow depth of field. No people in the room, only the clipping.")
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
