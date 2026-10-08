"""6 enrichment still-life / atmosphere images. Objects only, no people, no blood.
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_enrich.py
"""
import os, sys, json, base64, time, urllib.request, urllib.error
from pathlib import Path
API_KEY=os.environ.get("OPENAI_API_KEY")
if not API_KEY: print("ERROR"); sys.exit(1)
OUTPUT_DIR=Path(__file__).parent.parent/"images"
LOG=OUTPUT_DIR/"_enrich.log"
BASE=("Film still / cinematic still-life from a 1994 neo-noir character drama set in New York City. "
      "35mm film grain, low-key chiaroscuro lighting, vignetting. Warm desaturated cream, beige, olive tones. "
      "Practical lighting only — tungsten lamp, window light. No modern elements. No text, no captions, no watermarks. ")
# objects allowed; ban people / blood / violence
NEG=(" Absolutely no: people, human figures, hands, faces, blood, gore, violence, text overlays, logos, "
     "watermarks, smartphones, modern vehicles, digital screens, cartoon, anime, 3D render, glossy CGI, "
     "plastic look, oversaturation, HDR.")
IMAGES=[
 {"filename":"beretta_parts.png","subject":(
   "Overhead still-life: a handgun fully disassembled into its parts — slide, barrel, recoil spring, "
   "magazine, frame — laid out in a neat row on an oily grey cleaning cloth on a dark wooden table, "
   "lit by a single warm pendant lamp. Methodical, clinical, intimate. No hands, no people. Deep shadow.")},
 {"filename":"clue_milk_glass.png","subject":(
   "Close-up still-life: a single tall glass of milk on a worn wooden table catching warm tungsten "
   "lamplight, faint condensation on the glass, deep shadow all around. Quiet, solitary, a little sad. No people.")},
 {"filename":"door_chain.png","subject":(
   "Close-up of a chained apartment door inside a dim 1990s tenement at night: a taut brass door chain "
   "across the gap, and a thin blade of warm hallway light slipping through. Tension, a threshold, the "
   "moment before a decision. No people. Heavy shadow, vignetting.")},
 {"filename":"shattered_glass.png","subject":(
   "A shattered glass office door, jagged fragments scattered and suspended across a polished marble "
   "floor catching cold light, a warm lamp glow beyond. The aftermath of a sudden violent motion — but "
   "no people and no blood, only flying glass. Dynamic, tense, cinematic. Desaturated cool-warm palette.")},
 {"filename":"office_night.png","subject":(
   "A cold sterile government office floor at night seen down a long empty corridor: rows of empty desks, "
   "venetian blinds, one flickering fluorescent panel, cold blue light pooling on the floor. Clinical, "
   "oppressive, abandoned. No people. Cinematic noir, vignetting. Desaturated blue-grey palette.")},
 {"filename":"casings_marble.png","subject":(
   "Close-up still-life: a scatter of brass shell casings on a polished marble lobby floor catching warm "
   "lamplight, thin pale smoke haze drifting above them, a toppled potted plant blurred in the background. "
   "Aftermath and stillness. No people, no blood. Cinematic noir. Warm-grey palette.")},
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
