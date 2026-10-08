"""Regenerate leon_reading.png — the paper must clearly read the name "LEON". Overwrites.
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_reading2.py
"""
import os, sys, json, base64, time, urllib.request, urllib.error
from pathlib import Path
API_KEY=os.environ.get("OPENAI_API_KEY")
if not API_KEY: print("ERROR"); sys.exit(1)
OUT=Path(__file__).parent.parent/"images"/"leon_reading.png"
BASE=("Film still from a 1994 character drama set in a cozy Little Italy apartment. 35mm film grain, soft "
      "warm tungsten lamplight, vignetting. Warm desaturated cream and amber tones. No watermarks, no logos. ")
NEG=(" Absolutely no: smartphones, modern vehicles, digital screens, cartoon, anime, 3D render, glossy CGI, "
     "plastic skin, oversaturation, HDR, weapons, blood, violence, minors. No other words or letters anywhere "
     "except the single name on the paper.")
SUBJECT=("Tender close-up over a small wooden kitchen table under a single warm lamp: an adult man's "
         "weathered hand and a young woman's smaller hand near a torn scrap of brown paper. On the paper, "
         "ONE single word is written by hand in large, careful, slightly childlike pencil block letters: "
         "the name \"LEON\" — spelled L, E, O, N. The man's fingertip rests just beneath the letters as he "
         "slowly learns to read his own name. Intimate, domestic, warm. Shallow depth of field. "
         "Only the word LEON appears on the paper, nothing else written.")
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
