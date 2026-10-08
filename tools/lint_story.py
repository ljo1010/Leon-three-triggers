# -*- coding: utf-8 -*-
"""LÉON story integrity linter.
Scans all .twee passages for:
  - block-macro open/close balance & nesting (timed, type, gate, link, if, nobr, silently, button, linkappend...)
  - <<next>> usage outside <<timed>>
  - unresolved link/goto/pick/gate targets
  - missing image files referenced by <img src="images/...">
Read-only. Prints a report; exit code 1 if any error found.
"""
import re, sys, glob, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
IMG = os.path.join(ROOT, "images")

# container macros that require a matching close tag
CONTAINERS = ["timed", "type", "gate", "link", "if", "nobr", "silently",
              "button", "linkappend", "linkreplace", "append", "replace",
              "for", "switch", "capture", "widget"]

passages = {}   # name -> (file, body)
def load():
    files = glob.glob(os.path.join(SRC, "*.twee")) + glob.glob(os.path.join(SRC, "passages", "*.twee"))
    for f in files:
        txt = open(f, encoding="utf-8").read()
        # split on lines beginning with ::
        parts = re.split(r"(?m)^::[ \t]+", txt)
        for chunk in parts[1:]:
            header, _, body = chunk.partition("\n")
            name = header.split("[")[0].split("{")[0].strip()
            # strip comments so doc-text macros aren't counted
            body = re.sub(r"/\*.*?\*/", "", body, flags=re.S)   # /* TwineScript */
            body = re.sub(r"/%.*?%/", "", body, flags=re.S)     # /% SugarCube %/
            body = re.sub(r"<!--.*?-->", "", body, flags=re.S)  # html
            passages[name] = (os.path.basename(f), body)

def check_macro_balance(name, body):
    errs = []
    # tokenize macro tags
    toks = re.findall(r"<<\s*/?\s*([A-Za-z][\w]*)", body)
    # rebuild with close-info
    raw = re.findall(r"<<\s*(/?)\s*([A-Za-z][\w]*)", body)
    stack = []
    for closing, mac in raw:
        if mac == "next":
            if "timed" not in stack:
                errs.append(f"<<next>> outside <<timed>>")
            continue
        if mac == "else" or mac == "elseif":
            continue
        if mac not in CONTAINERS:
            continue
        if closing:
            if not stack:
                errs.append(f"<</{mac}>> with no open")
            elif stack[-1] != mac:
                errs.append(f"<</{mac}>> but innermost open is <<{stack[-1]}>>")
                # pop anyway to continue
                if mac in stack:
                    while stack and stack[-1] != mac:
                        stack.pop()
                    if stack: stack.pop()
            else:
                stack.pop()
        else:
            stack.append(mac)
    for leftover in stack:
        errs.append(f"<<{leftover}>> never closed")
    return errs

def check_links(name, body, defined):
    errs = []
    targets = []
    # [[label|Target]] and [[Target]]
    for m in re.finditer(r"\[\[([^\]]+?)\]\]", body):
        inner = m.group(1)
        inner = inner.split("][")[0]  # strip setter [[..|T][setter]]
        if "|" in inner:
            t = inner.split("|")[-1]
        elif "->" in inner:
            t = inner.split("->")[-1]
        elif "<-" in inner:
            t = inner.split("<-")[0]
        else:
            t = inner
        targets.append(t.strip())
    # <<pick "Target" ...>>  and <<gate "stat" n "Target" ...>>
    for m in re.finditer(r"<<pick\s+(\"[^\"]+\"|'[^']+')", body):
        targets.append(m.group(1)[1:-1])
    for m in re.finditer(r"<<gate\s+\"[^\"]+\"\s+\S+\s+\"([^\"]+)\"", body):
        targets.append(m.group(1))
    for m in re.finditer(r"<<goto\s+(\"[^\"]+\"|'[^']+')", body):
        targets.append(m.group(1)[1:-1])
    for t in targets:
        if t and t not in defined:
            errs.append(f"link target not found: '{t}'")
    return errs

def check_images(name, body):
    errs = []
    for m in re.finditer(r'src="images/([^"]+)"', body):
        p = os.path.join(IMG, m.group(1))
        if not os.path.exists(p):
            errs.append(f"missing image: images/{m.group(1)}")
    return errs

def main():
    load()
    defined = set(passages.keys())
    total = 0
    for name, (f, body) in passages.items():
        errs = []
        errs += check_macro_balance(name, body)
        errs += check_links(name, body, defined)
        errs += check_images(name, body)
        if errs:
            total += len(errs)
            print(f"\n[{f}] :: {name}")
            for e in errs:
                print(f"    - {e}")
    print(f"\n=== passages: {len(passages)} | issues: {total} ===")
    sys.exit(1 if total else 0)

main()
