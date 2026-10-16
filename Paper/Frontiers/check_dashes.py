text = open("CivicWorkOS_supplementary.tex", encoding="utf-8").read()

import re

# check for unicode dashes
for idx, line in enumerate(text.splitlines(), 1):
    if "—" in line:
        print(f"L{idx} em-dash (—): {line}")
    if "–" in line:
        # check if not a number range like 10–20 or citation
        # find where – is used
        matches = re.finditer(r"[^\d\s]–[^\d\s]", line)
        for m in matches:
            print(f"L{idx} en-dash between letters: {line}")
