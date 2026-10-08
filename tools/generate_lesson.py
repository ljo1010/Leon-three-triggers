"""Regenerate mathilda_training.png — intimate FIRST gun lesson at the kitchen table (not a range).
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_lesson.py
"""
import os, sys, json, base64, time, urllib.request, urllib.error
from pathlib import Path
API_KEY=os.environ.get("OPENAI_API_KEY")
if not API_KEY: print("ERROR"); sys.exit(1)
OUT=Path(__file__).parent.parent/"images"/"mathilda_training.png"
BASE=("Film still from a 1994 neo-noir character drama set in a small tenement apartment. 35mm film grain, "
      "low-key warm tungsten lighting from a single pendant lamp, cinematic, vignetting. Warm desaturated "
      "amber and cream tones. No modern elements. No text, no captions, no watermarks. ")
NEG=(" Absolutely no: shooting range, gun range, indoor range, ear protectors, ear muffs, safety goggles, "
     "safety glasses, aiming, pointing the weapon, threatening pose, muzzle flash, logos, watermarks, "
     "smartphones, modern vehicles, digital screens, cartoon, anime, 3D render, glossy CGI, plastic skin, "
     "oversaturation, HDR, blood, violence, children, minors.")
SUBJECT=("Intimate low-key close-up at a dark wooden kitchen table at night under one warm pendant lamp. "
         "An adult man's weathered hands gently guide a young woman's smaller hands as they hold a handgun "
         "together on the table, his fingertip showing her the safety catch. The framing centers on the "
         "four hands and the pistol resting on the wood; an oily cleaning cloth and a few disassembled "
         "parts lie beside them. A first, careful, tender lesson at home — quiet and domestic, NOT a "
         "shooting range. Deep shadow, warm amber light, shallow depth of field. Documentary realism.")
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
