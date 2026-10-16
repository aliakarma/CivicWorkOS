import re
text = open("CivicWorkOS_supplementary.tex", encoding="utf-8").read()

for idx, line in enumerate(text.splitlines(), 1):
    # find -- not part of --- and not between numbers like 10--20
    # and not in LaTeX commands
    line_clean = re.sub(r"---", "", line)
    for m in re.finditer(r"(?<![0-9])--(?![\d\>])", line_clean):
        # ignore \addplot coordinates or comments
        if line.strip().startswith("%"):
            continue
        print(f"L{idx} en-dash (--): {line.strip()}")
