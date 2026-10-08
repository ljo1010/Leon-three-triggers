"""Regenerate mathilda_in_apartment.png — softer, more feminine Mathilda. Overwrites same file.
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_mathilda_fem.py
"""
import os, sys, json, base64, time, urllib.request, urllib.error
from pathlib import Path
API_KEY=os.environ.get("OPENAI_API_KEY")
if not API_KEY: print("ERROR"); sys.exit(1)
OUT=Path(__file__).parent.parent/"images"/"mathilda_in_apartment.png"
BASE=("Film still from a 1994 neo-noir character drama set in New York City. 35mm film grain, low-key "
      "warm tungsten lighting, cinematic, vignetting. Warm desaturated cream and amber tones. "
      "Practical lamp and window light. No modern elements. No text, no captions, no watermarks. ")
NEG=(" Absolutely no: masculine or mannish features, square jaw, beard, stubble, logos, watermarks, "
     "smartphones, modern vehicles, digital screens, cartoon, anime, 3D render, glossy CGI, plastic skin, "
     "oversaturation, HDR, weapons, blood, violence, children, minors.")
SUBJECT=("A delicate, soft, clearly feminine young woman in her early twenties with gentle graceful "
         "features, large expressive eyes, and a neat glossy dark bob with blunt bangs. She stands in "
         "profile by a tall window in a warm dim 1990s tenement apartment, gazing out at the city. She "
         "wears a soft oversized knit sweater and a thin black velvet choker; slender, graceful posture, "
         "hands gently clasped. On the windowsill, a small potted green plant and a paper milk carton. "
         "A warm tungsten lamp glows in the background. Melancholy, tender, vulnerable. Shallow depth of "
         "field, documentary realism, no glamour. Warm cream and amber palette.")
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
        print(f"a{a} HTTP {e.code}: {e.read().decode('utf-8','replace')[:200]}")
        if e.code in (500,502,503,520) and a<3: time.sleep(5); continue
        break
    except Exception as e:
        print(f"a{a} ERR {e}")
        if a<3: time.sleep(5); continue
        break
