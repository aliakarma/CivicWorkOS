#!/usr/bin/env python3
"""Body-word count of the main article on the basis Frontiers declares.

texcount's text total already leaves out section titles, captions and
references; the author guidelines further exclude the abstract, the
acknowledgment and the funding statement. This prints that figure, which is
the number \\extraAuth must state.

    python count_words.py [CivicWorkOS.tex]          # prints the count
    python count_words.py --detail [CivicWorkOS.tex] # and its parts
"""
import os
import re
import subprocess
import sys
import tempfile


def texcount(path):
    out = subprocess.run(["texcount", "-inc", "-total", "-q", "-1", path],
                         capture_output=True, text=True, check=True).stdout
    return int(out.split("+")[0].strip())


def count_fragment(text):
    f = tempfile.NamedTemporaryFile("w", suffix=".tex", delete=False, encoding="utf-8")
    try:
        f.write(text)
        f.close()
        return texcount(f.name)
    finally:
        os.unlink(f.name)


def main(argv):
    detail = "--detail" in argv
    args = [a for a in argv if a != "--detail"]
    path = args[0] if args else "CivicWorkOS.tex"
    src = open(path, encoding="utf-8").read()

    excluded = {
        "abstract": re.search(r"\\begin\{abstract\}(.*?)\\tiny", src, re.S).group(1),
    }
    for name in ("Acknowledgment", "Funding"):
        m = re.search(r"\\section\*\{" + name + r"\}(.*?)(?=\\section)", src, re.S)
        if m is None:
            sys.exit(f"count_words.py: no \\section*{{{name}}} in {path}")
        excluded[name.lower()] = m.group(1)

    total = texcount(path)
    parts = {k: count_fragment(v) for k, v in excluded.items()}
    basis = total - sum(parts.values())
    if detail:
        print(f"texcount total {total}; excluded {parts}; journal basis {basis}")
    else:
        print(basis)


if __name__ == "__main__":
    main(sys.argv[1:])
