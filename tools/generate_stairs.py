"""leon_stairs.png — Leon (from behind) watching the stairwell. Replaces leon_stairs_mathilda usage.
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_stairs.py
"""
import os, sys, json, base64, time, urllib.request, urllib.error
from pathlib import Path
API_KEY=os.environ.get("OPENAI_API_KEY")
if not API_KEY: print("ERROR"); sys.exit(1)
OUT=Path(__file__).parent.parent/"images"/"leon_stairs.png"
BASE=("Film still from a 1994 neo-noir character drama. 35mm film grain, low-key chiaroscuro, vignetting. "
      "Warm desaturated amber, cream and deep-shadow tones. Practical light only — a single bare hanging "
      "bulb. No modern elements. No text, no captions, no watermarks. ")
NEG=(" Absolutely no: fedora, brimmed hat, wide-brim hat, text, logos, watermarks, smartphones, modern "
     "vehicles, digital screens, cartoon, anime, 3D render, glossy CGI, plastic skin, oversaturation, HDR, "
     "weapons, guns, blood, violence, children, minors.")
SUBJECT=("Seen from behind: a solitary man in a long dark wool overcoat and a snug black knit beanie "
         "(rounded, no brim) stands in his half-open apartment doorway at night, his broad still back to "
         "the camera, looking out into a dim 1990s tenement stairwell lit by a single bare hanging bulb. "
         "Iron stair railings cast long shadows across the walls. Far down at the foot of the stairs, a "
         "small dim hunched figure sits in shadow beside a fallen milk carton, barely visible. The man's "
         "silhouette dominates the foreground. Quiet, watchful, melancholy. Warm amber and deep shadow.")
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
