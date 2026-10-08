"""2 prop close-ups: prop_milk (shared milk cartons), prop_doll (little brother's doll).
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_props.py
"""
import os, sys, json, base64, time, urllib.request, urllib.error
from pathlib import Path
API_KEY=os.environ.get("OPENAI_API_KEY")
if not API_KEY: print("ERROR"); sys.exit(1)
OUTPUT_DIR=Path(__file__).parent.parent/"images"
LOG=OUTPUT_DIR/"_props.log"
BASE=("Cinematic still-life from a 1994 neo-noir character drama. 35mm film grain, low-key warm tungsten "
      "lighting, shallow depth of field, vignetting. Warm desaturated cream and amber tones. "
      "No modern elements. No text, no captions, no watermarks. ")
NEG=(" Absolutely no: people, human figures, hands, faces, blood, violence, text, logos, watermarks, "
     "smartphones, modern vehicles, digital screens, cartoon, anime, 3D render, glossy CGI, plastic look, "
     "oversaturation, HDR, children, minors.")
IMAGES=[
 {"filename":"prop_milk.png","subject":(
   "Two old paper milk cartons standing side by side on a dim, worn tenement stair step under a single "
   "warm bulb — one carton slightly larger than the other. Quiet symbolism of two strangers sharing the "
   "same small comfort. Soft warm light, deep shadow, intimate close-up. No people.")},
 {"filename":"prop_doll.png","subject":(
   "A small worn child's rag doll resting on the strap of an open schoolbag on a dim tenement stair, lit "
   "by a faint warm bulb. Tender and a little sad, a beloved keepsake. Soft focus background, deep "
   "shadow, intimate close-up. No people.")},
]
def log(m):
    line=f"[{time.strftime('%H:%M:%S')}] {m}"; print(line,flush=True)
    with open(LOG,"a",encoding="utf-8") as f: f.write(line+"\n")
def gen(it,i,n):
    prompt=BASE+" Subject: "+it["subject"]+NEG
    out=OUTPUT_DIR/it["filename"]; log(f"[{i}/{n}] {it['filename']}")
    payload=json.dumps({"model":"gpt-image-1","prompt":prompt,"n":1,"size":"1536x1024","quality":"high"}).encode()
    for a in range(1,4):
        req=urllib.request.Request("https://api.openai.com/v1/images/generations",data=payload,
            headers={"Authorization":f"Bearer {API_KEY}","Content-Type":"application/json"},method="POST")
        s=time.time()
        try:
            with urllib.request.urlopen(req,timeout=300) as r: d=json.loads(r.read().decode())
            out.write_bytes(base64.b64decode(d["data"][0]["b64_json"])); log(f"[{i}/{n}] OK ({time.time()-s:.1f}s)"); return True
        except urllib.error.HTTPError as e:
            log(f"[{i}/{n}] a{a} HTTP {e.code}: {e.read().decode('utf-8','replace')[:200]}")
            if e.code in (500,502,503,520) and a<3: time.sleep(5); continue
            return False
        except Exception as e:
            log(f"[{i}/{n}] a{a} ERR {e}")
            if a<3: time.sleep(5); continue
            return False
ok=0
for i,it in enumerate(IMAGES,1):
    if gen(it,i,len(IMAGES)): ok+=1
    time.sleep(1)
log(f"=== Done {ok}/{len(IMAGES)} ===")
