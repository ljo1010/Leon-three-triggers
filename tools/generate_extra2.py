"""2 scenes: stansfield_tony (interrogation), sniper_lesson (rooftop overwatch teaching).
   Policy-safe: no visible weapons, no menacing pose, adults only.
   Run:  OPENAI_API_KEY="sk-..." python tools/generate_extra2.py
"""
import os, sys, json, base64, time, urllib.request, urllib.error
from pathlib import Path
API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY: print("ERROR"); sys.exit(1)
OUTPUT_DIR = Path(__file__).parent.parent / "images"
LOG = OUTPUT_DIR / "_extra2.log"
BASE = ("Film still from a 1994 neo-noir character drama set in New York City. 35mm film grain, low-key "
        "chiaroscuro lighting, cinematic letterbox, vignetting. Warm desaturated cream, beige, olive tones. "
        "Practical lighting only. No modern elements. No text, no captions, no watermarks. ")
NEG = (" Absolutely no: fedora, brimmed hat, text overlays, logos, watermarks, smartphones, modern vehicles, "
       "digital screens, cartoon, anime, 3D render, glossy CGI, plastic skin, oversaturation, HDR, weapons, "
       "guns, rifles, firearms, blood, violence, menacing expression, threatening pose, children, minors.")
IMAGES = [
  {"filename":"stansfield_tony.png","subject":(
      "Inside a dim, empty Little Italy family restaurant before opening hours. An older heavyset "
      "Italian-American restaurateur sits tense at his checkered-cloth table, both hands flat on a folded "
      "newspaper, jaw set. A composed lean man in a dark suit with a loosened tie stands calmly beside the "
      "table, looking down at him — a cold, quiet, unhurried confrontation, detached rather than aggressive. "
      "Shelves of wine bottles and warm wall lamps behind them. Heavy tense stillness. No weapons.")},
  {"filename":"sniper_lesson.png","subject":(
      "Two figures on a city rooftop at dusk. An adult man in a snug black knit beanie kneels close behind a "
      "young woman in her early twenties, gently guiding her shoulders and posture as she leans on the rooftop "
      "ledge looking through a long black spotting scope toward a distant glittering skyline. An open dark "
      "equipment case rests beside them. Concentration, mentorship, quiet trust. Wind moves their clothes. "
      "Golden-blue dusk light, deep shadows. No weapons.")},
]
def log(m):
    line=f"[{time.strftime('%H:%M:%S')}] {m}"; print(line,flush=True)
    with open(LOG,"a",encoding="utf-8") as f: f.write(line+"\n")
def gen(it,i,n):
    prompt=BASE+" Subject: "+it["subject"]+NEG
    out=OUTPUT_DIR/it["filename"]
    log(f"[{i}/{n}] {it['filename']}")
    payload=json.dumps({"model":"gpt-image-1","prompt":prompt,"n":1,"size":"1536x1024","quality":"high"}).encode()
    for a in range(1,4):
        req=urllib.request.Request("https://api.openai.com/v1/images/generations",data=payload,
            headers={"Authorization":f"Bearer {API_KEY}","Content-Type":"application/json"},method="POST")
        s=time.time()
        try:
            with urllib.request.urlopen(req,timeout=300) as r: d=json.loads(r.read().decode())
            out.write_bytes(base64.b64decode(d["data"][0]["b64_json"]))
            log(f"[{i}/{n}] OK ({time.time()-s:.1f}s)"); return True
        except urllib.error.HTTPError as e:
            log(f"[{i}/{n}] a{a} HTTP {e.code}: {e.read().decode('utf-8','replace')[:200]}")
            if e.code in (500,502,503,520) and a<3: time.sleep(5); continue
            return False
        except Exception as e:
            log(f"[{i}/{n}] a{a} ERR {e}");
            if a<3: time.sleep(5); continue
            return False
ok=0
for i,it in enumerate(IMAGES,1):
    if gen(it,i,len(IMAGES)): ok+=1
    time.sleep(1)
log(f"=== Done {ok}/{len(IMAGES)} ===")
