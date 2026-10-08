"""TEST gpt-image-2 on the main images -> saved as *_img2.png (originals untouched).
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_img2_test.py
"""
import os, sys, json, base64, time, urllib.request, urllib.error
from pathlib import Path
API_KEY=os.environ.get("OPENAI_API_KEY")
if not API_KEY: print("ERROR"); sys.exit(1)
OUTPUT_DIR=Path(__file__).parent.parent/"images"
LOG=OUTPUT_DIR/"_img2.log"
MODEL="gpt-image-2"
BASE=("Film still from a 1994 neo-noir character drama set in New York City. 35mm film grain, low-key "
      "chiaroscuro lighting, cinematic letterbox composition, vignetting. Warm desaturated cream, beige and "
      "dusty olive tones. Practical tungsten/window light. No modern elements. No text, no watermarks. ")
NEG=(" Absolutely no: text, logos, watermarks, smartphones, modern vehicles, digital screens, cartoon, "
     "anime, 3D render, glossy CGI, plastic skin, oversaturation, HDR, weapons, blood, violence, children, "
     "minors. Do NOT depict any real or recognizable actor; original fictional faces only.")
LEON=("a lean solitary man in his late thirties, short dark hair, stubble, small round dark sunglasses, ")
IMAGES=[
 {"filename":"title_img2.png","subject":(
   "Strong backlit rim-light silhouette of " + LEON + "and a snug black knit beanie (rounded, no brim) and "
   "a long dark overcoat. He stands in a narrow dark 1990s tenement corridor with warm light flooding from "
   "a window behind, his whole outline glowing. Cinematic poster-like negative space. Solitary, iconic.")},
 {"filename":"leon_portrait_img2.png","subject":(
   "Tight three-quarter character portrait of " + LEON + "with a lean weathered face and quiet melancholy "
   "eyes looking off toward a window. Small round dark sunglasses pushed up on his forehead, plain beige "
   "knit sweater with a thin dark leather strap across it. Sparse 1990s tenement apartment, warm tungsten "
   "lamp from one side, the other half of his face in deep shadow. Solitary, contained, documentary realism.")},
 {"filename":"mathilda_portrait_img2.png","subject":(
   "Character portrait of a delicate, clearly feminine young woman in her early twenties with large "
   "expressive eyes and a neat glossy dark bob with blunt bangs. A soft, wary, melancholy look. She wears a "
   "knit top and a thin black velvet choker, in a dim warm 1990s tenement apartment lit by a single lamp. "
   "Vulnerable yet resolute. Warm cream and amber palette, shallow depth of field.")},
 {"filename":"stansfield_face_img2.png","subject":(
   "Tight close-up portrait of an original fictional corrupt official in his early forties: a gaunt, pale, "
   "sweat-sheened face, damp disheveled dark hair, day-old stubble, wild glassy heavy-lidded eyes with a "
   "cold drugged stare into the camera. Rumpled dark 1990s suit, loosened tie. Harsh raking side light, "
   "deep shadow, sickly warm green-amber grade. Barely-contained manic intensity.")},
]
def log(m):
    line=f"[{time.strftime('%H:%M:%S')}] {m}"; print(line,flush=True)
    with open(LOG,"a",encoding="utf-8") as f: f.write(line+"\n")
def gen(it,i,n):
    prompt=BASE+" Subject: "+it["subject"]+NEG
    out=OUTPUT_DIR/it["filename"]; log(f"[{i}/{n}] {MODEL} -> {it['filename']}")
    payload=json.dumps({"model":MODEL,"prompt":prompt,"n":1,"size":"1536x1024","quality":"high"}).encode()
    for a in range(1,3):
        req=urllib.request.Request("https://api.openai.com/v1/images/generations",data=payload,
            headers={"Authorization":f"Bearer {API_KEY}","Content-Type":"application/json"},method="POST")
        s=time.time()
        try:
            with urllib.request.urlopen(req,timeout=300) as r: d=json.loads(r.read().decode())
            out.write_bytes(base64.b64decode(d["data"][0]["b64_json"])); log(f"[{i}/{n}] OK ({time.time()-s:.1f}s)"); return True
        except urllib.error.HTTPError as e:
            body=e.read().decode('utf-8','replace')[:400]
            log(f"[{i}/{n}] HTTP {e.code}: {body}")
            if e.code in (500,502,503,520) and a<2: time.sleep(5); continue
            return False
        except Exception as e:
            log(f"[{i}/{n}] ERR {type(e).__name__}: {e}"); return False
ok=0
for i,it in enumerate(IMAGES,1):
    if gen(it,i,len(IMAGES)): ok+=1
    time.sleep(1)
log(f"=== Done {ok}/{len(IMAGES)} ({MODEL}) ===")
