"""school_office.png — Mathilda confessing to the stern headmistress. Safe.
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_office.py
"""
import os, sys, json, base64, time, urllib.request, urllib.error
from pathlib import Path
API_KEY=os.environ.get("OPENAI_API_KEY")
if not API_KEY: print("ERROR"); sys.exit(1)
OUT=Path(__file__).parent.parent/"images"/"school_office.png"
BASE=("Film still from a 1994 character drama. 35mm film grain, soft warm window light, cinematic, "
      "vignetting. Warm desaturated cream and amber tones. No modern elements. No text, no watermarks. ")
NEG=(" Absolutely no: logos, watermarks, smartphones, modern vehicles, digital screens, cartoon, anime, "
     "3D render, glossy CGI, plastic skin, oversaturation, HDR, weapons, blood, violence, minors.")
SUBJECT=("A wood-paneled private school office in the afternoon. A stern, dignified older woman with "
         "glasses sits behind a large desk, looking up. Before the desk stands a young woman in her early "
         "twenties with short dark bobbed hair, seen from behind and slightly to the side, shoulders "
         "lowered, vulnerable but resolute as she speaks. Soft light from a tall window, bookshelves, a "
         "quiet emotional tension of a confession and a plea. Shallow depth of field. Warm cream palette.")
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
