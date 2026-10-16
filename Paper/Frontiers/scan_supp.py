import re

text = open("CivicWorkOS_supplementary.tex", encoding="utf-8").read()

patterns = {
    "show its working": r"\bshow\s+its\s+working\b",
    "afterwards": r"\bafterwards\b",
    "towards": r"\btowards\b",
    "judgement": r"\bjudgement\b",
    "centre": r"\bcentre\b",
    "behaviour": r"\bbehaviour\b",
    "programme": r"\bprogramme\b",
    "modelling": r"\bmodelling\b",
    "multi-dimensional": r"\bmulti-dimensional\b",
    "em-dash (---)": r"---",
    "bare cite": r"\\cite\{",
    "bare eqref": r"(?<!Equation~)(?<!equation~)(?<!Eq\.~)(?<!eq\.~)(?<!under~)(?<!through~)(?<!of~)(?<!in~)(?<!from~)(?<!with~)\\eqref\{",
}

for name, p in patterns.items():
    matches = list(re.finditer(p, text, re.I))
    print(f"{name}: {len(matches)} matches")
    for m in matches[:6]:
        line_no = text[:m.start()].count("\n") + 1
        start = max(0, m.start() - 35)
        end = min(len(text), m.end() + 35)
        snippet = text[start:end].replace("\n", " ")
        print(f"   L{line_no} [{m.group()}]: ...{snippet}...")
