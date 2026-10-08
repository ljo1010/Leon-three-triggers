"""Regenerate leon_confession.png — Leon as a lean, weathered hitman (not a gentle uncle). Overwrites.
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_confession2.py
"""
import os, sys, json, base64, time, urllib.request, urllib.error
from pathlib import Path
API_KEY=os.environ.get("OPENAI_API_KEY")
if not API_KEY: print("ERROR"); sys.exit(1)
OUT=Path(__file__).parent.parent/"images"/"leon_confession.png"
BASE=("Tight low-key cinematic character portrait, film still from a 1994 neo-noir drama. 35mm film grain, "
      "warm tungsten side lamplight with deep shadow, vignetting. Warm desaturated cream and shadow tones. "
      "No modern elements. No text, no watermarks. ")
NEG=(" Absolutely no: soft round friendly face, gentle smile, kindly uncle look, plump cheeks, clean-shaven "
     "baby face, weapons, guns, blood, violence, text, logos, watermarks, smartphones, cartoon, anime, 3D "
     "render, glossy CGI, plastic skin, oversaturation, HDR, children, minors. Do NOT depict any real or "
     "recognizable actor; original fictional face.")
SUBJECT=("An original fictional lean, weathered, hard-faced solitary hitman in his late thirties: short "
         "dark hair, several days of dark stubble, sharp gaunt features, a wiry build, and a quiet "
         "dangerous stillness. Small round dark sunglasses are pushed up on his forehead. He wears a plain "
         "beige knit sweater with a thin dark leather strap across it. He sits at a small wooden kitchen "
         "table in a dim, sparse 1990s tenement apartment, head slightly bowed, melancholy downcast eyes — "
         "a professional killer's restraint cracking just a little as he speaks of his past. One side of "
         "his face lit by a warm lamp, the rest in deep shadow; a cup of coffee on the table. Solitary, "
         "contained, hardened. Documentary realism, no glamour, not soft or gentle.")
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
