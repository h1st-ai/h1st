# This script remove submodules and subpackages 
# from the documentation title

from pathlib import Path

src_dir = Path("source/api")
for file in src_dir.iterdir():
    print("Processed RST file:", file)
    with open(file, "r") as f:
        lines = f.read()

    junk_strs = ["Submodules\n----------", "Subpackages\n-----------"]

    for junk in junk_strs:
        lines = lines.replace(junk, "")

    lines = lines.replace(" module\n=", "\n")

    with open(file, "w") as f:
        f.write(lines)