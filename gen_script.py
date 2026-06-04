import os, json, sys
workdir = os.path.dirname(os.path.abspath(__file__))
savedir = os.path.join(workdir, "screenshots")
os.makedirs(savedir, exist_ok=True)

with open(os.path.join(workdir, "build_s1_content.txt"), "r", encoding="utf-8") as f:
    script = f.read()

outpath = os.path.join(workdir, "build_s1_hero.py")
with open(outpath, "w", encoding="utf-8") as f:
    f.write(script)
print("Generated:", outpath)
