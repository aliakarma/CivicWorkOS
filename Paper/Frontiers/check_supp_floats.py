import re

text = open("CivicWorkOS_supplementary.tex", encoding="utf-8").read()

floats = re.findall(r"\\begin\{(table|figure)\}.*?\\label\{([^}]+)\}", text, re.S)
print(f"Total floats: {len(floats)}")
for ftype, label in floats:
    # find where label is declared
    decl_pos = text.find(f"\\label{{{label}}}")
    # find all references to label
    refs = [m.start() for m in re.finditer(rf"\\ref\{{{label}\}}", text)]
    first_ref = min(refs) if refs else None
    decl_line = text[:decl_pos].count("\n") + 1
    ref_line = text[:first_ref].count("\n") + 1 if first_ref is not None else None
    
    status = "OK (declared after ref)" if (first_ref is not None and decl_pos > first_ref) else ("NO REFS" if first_ref is None else "VIOLATION (declared before ref)")
    print(f"[{ftype}] label: {label} | Declared L{decl_line} | First Ref L{ref_line} | Status: {status}")
