"""leon_reading.png — Mathilda teaching Leon to read (literacy bonding). Hands-focused, safe.
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_reading.py
"""
import os, sys, json, base64, time, urllib.request, urllib.error
from pathlib import Path
API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY: print("ERROR"); sys.exit(1)
OUT = Path(__file__).parent.parent / "images" / "leon_reading.png"
BASE = ("Film still from a 1994 neo-noir character drama set in Little Italy, New York City. "
        "Shot on 35mm film with subtle grain, warm low-key tungsten lamplight. Cinematic, vignetting. "
        "Warm desaturated cream, beige and amber tones. Practical lamp light. No modern elements. "
        "No text that is readable, no captions, no watermarks. ")
NEG = (" Absolutely no: logos, watermarks, smartphones, modern vehicles, digital screens, cartoon, anime, "
       "3D render, glossy CGI, plastic skin, oversaturation, HDR, weapons, guns, blood, violence, minors.")
SUBJECT = ("Tender close-up over a small wooden kitchen table under a single warm lamp: an adult man's "
           "weathered hand and a young woman's smaller hand together near a torn scrap of paper covered "
           "in large, careful handwritten letters made with a pencil. The man's fingertip rests under the "
           "letters as he slowly learns to read them. Intimate, domestic, quiet warmth — a hardened man "
           "being taught something gentle. Shallow depth of field. Warm cream and amber palette.")
prompt = BASE + " Subject: " + SUBJECT + NEG
payload = json.dumps({"model":"gpt-image-1","prompt":prompt,"n":1,"size":"1536x1024","quality":"high"}).encode()
for attempt in range(1,4):
    req = urllib.request.Request("https://api.openai.com/v1/images/generations", data=payload,
        headers={"Authorization": f"Bearer {API_KEY}","Content-Type":"application/json"}, method="POST")
    s=time.time()
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            d=json.loads(r.read().decode())
        OUT.write_bytes(base64.b64decode(d["data"][0]["b64_json"]))
        print(f"OK ({time.time()-s:.1f}s) -> {OUT.name}"); break
    except urllib.error.HTTPError as e:
        print(f"attempt {attempt} HTTP {e.code}: {e.read().decode('utf-8','replace')[:200]}")
        if e.code in (500,502,503,520) and attempt<3: time.sleep(5); continue
        break
    except Exception as e:
        print(f"attempt {attempt} ERR {e}")
        if attempt<3: time.sleep(5); continue
        break
