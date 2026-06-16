# -*- coding: utf-8 -*-
import os, zipfile
d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples")
out_path = os.path.join(d, "extracted.txt")
with open(out_path, "w", encoding="utf-8") as out:
    for z in ["card_sample.zip", "note_sample.zip"]:
        p = os.path.join(d, z)
        out.write("===== " + z + " =====\n")
        if not os.path.exists(p):
            out.write("(not found)\n\n")
            continue
        zf = zipfile.ZipFile(p)
        out.write("entries: " + ", ".join(zf.namelist()) + "\n")
        out.write("--- data.xml ---\n")
        out.write(zf.read("data.xml").decode("utf-8"))
        out.write("\n\n")
print("done")
