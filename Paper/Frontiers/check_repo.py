#!/usr/bin/env python3
"""check_repo.py -- repository/manuscript reconciliation gates (Phase 3).

The revision programme's Phase 3 goal is that a reviewer who follows the Data
Availability link finds a repository that describes *this* paper, credits *these*
authors, and whose verification script passes against the numbers *this* paper
prints. Three of those conditions are mechanically checkable, and this script
checks them:

  A. every manuscript label the repository cites resolves in the compiled
     article (or its supplement);
  B. no numbered manuscript reference survives anywhere in the repository;
  C. the author list is identical in README.md, CITATION.cff and \\def\\Authors.

Why A and B rather than "fix the numbers". Three findings in Phase 3 had the
same shape: the repository documented a paper that no longer existed, because
section and equation numbers moved underneath it. The article has now carried
three different numberings, and Phase 4 will produce a fourth. Numbered
citations are therefore treated as a defect, and the repository cites the
manuscript by LaTeX label instead -- labels are stable across every renumbering
that remains. Gate A is what makes that convention worth something: without it,
a mistyped or deleted label is just as silent as a stale number was.

    python check_repo.py           # full report
    python check_repo.py --quiet   # failures only

Exit status 0 when every gate passes.
"""

from __future__ import annotations

import argparse
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))

AUX_FILES = [
    os.path.join(HERE, "CivicWorkOS.aux"),
    os.path.join(HERE, "CivicWorkOS_supplementary.aux"),
]
TEX_FILES = [
    os.path.join(HERE, "CivicWorkOS.tex"),
    os.path.join(HERE, "CivicWorkOS_supplementary.tex"),
]

SCAN_EXT = (".py", ".md", ".yaml", ".yml", ".cff", ".toml", ".sh")
SKIP_DIRS = {
    "__pycache__", ".git", "Paper", ".mypy_cache", ".pytest_cache",
    ".ruff_cache", "node_modules", ".venv", "venv",
}

# A label-shaped citation in repository prose, e.g. `eq:cad`, `sec:worked`.
LABEL_RE = re.compile(r"\b((?:sec|eq|tab|fig|prop|app|alg):[A-Za-z0-9][A-Za-z0-9-]*)")

# A numbered manuscript reference, which the label convention replaces.
NUMBERED_RE = re.compile(
    r"\b(?:Paper |paper's own |article )?"
    r"(?:Sec\.|Section|§|Eq\.|Equation|Table|Fig\.|Figure|Prop\.|Proposition)"
    r"\s?\d+(?:\.\d+)*\b"
)

# Lines that legitimately contain a numbered reference and are not defects:
# this script's own patterns, and references to another repository document's
# own numbered sections rather than to the manuscript.
NUMBERED_ALLOW = re.compile(
    r"check_repo\.py|NUMBERED_RE|evaluation\.md\)? §|CONTRIBUTING\.md.{0,40}§"
)


def _read(path: str) -> str:
    return io.open(path, encoding="utf-8", errors="replace").read()


def known_labels() -> set[str]:
    """Every label the compiled article and its supplement define.

    Read from the .aux files, which record what actually compiled, and fall back
    to \\label{} in the sources when a document has not been built yet.
    """
    labels: set[str] = set()
    for aux in AUX_FILES:
        if os.path.isfile(aux):
            labels |= set(re.findall(r"\\newlabel\{([^}]+)\}", _read(aux)))
    for tex in TEX_FILES:
        if os.path.isfile(tex):
            labels |= set(re.findall(r"\\label\{([^}]+)\}", _read(tex)))
    return labels


def repo_files() -> list[str]:
    out = []
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in sorted(files):
            if f.endswith(SCAN_EXT):
                out.append(os.path.join(root, f))
    return out


def gate_labels_resolve(files: list[str]) -> list[str]:
    """A. Every cited label exists in the manuscript."""
    labels = known_labels()
    if not labels:
        return ["no manuscript labels found; build the article first"]
    problems = []
    for p in files:
        rel = os.path.relpath(p, REPO)
        for i, line in enumerate(_read(p).splitlines(), 1):
            for cited in LABEL_RE.findall(line):
                if cited not in labels:
                    problems.append(f"{rel}:{i}: unknown label {cited!r}")
    return problems


def gate_no_numbered_refs(files: list[str]) -> list[str]:
    """B. No numbered manuscript reference remains."""
    problems = []
    for p in files:
        rel = os.path.relpath(p, REPO)
        for i, line in enumerate(_read(p).splitlines(), 1):
            if NUMBERED_ALLOW.search(line):
                continue
            m = NUMBERED_RE.search(line)
            if m:
                problems.append(f"{rel}:{i}: numbered reference {m.group(0)!r}")
    return problems


def _manuscript_authors() -> list[str]:
    """Parse \\def\\Authors{...} into plain names, dropping affiliation marks."""
    tex = _read(TEX_FILES[0])
    m = re.search(r"\\def\\Authors\{(.*?)\n\}", tex, re.S)
    if not m:
        return []
    # Strip affiliation superscripts BEFORE splitting: "$^{1,2}$" holds a comma.
    body = re.sub(r"\$\^\{[^}]*\}\$", "", m.group(1))
    body = re.sub(r"\\[a-zA-Z]+", " ", body)              # \thanks and friends
    names = []
    for part in body.replace("~", " ").split(","):
        part = part.strip()
        if part:
            names.append(re.sub(r"\s+", " ", part))
    return names


def _readme_authors() -> list[str]:
    text = _read(os.path.join(REPO, "README.md"))
    m = re.search(r"theoretical framework by (.+?) \(\*Frontiers\*", text, re.S)
    if not m:
        return []
    raw = m.group(1).replace(" and ", ", ")
    return [n.strip() for n in raw.split(",") if n.strip()]


def _citation_authors() -> list[str]:
    text = _read(os.path.join(REPO, "CITATION.cff"))
    block = text.split("authors:", 1)
    if len(block) < 2:
        return []
    pairs = re.findall(
        r"- family-names:\s*(.+?)\n\s*given-names:\s*(.+?)\n", block[1]
    )
    return [f"{given.strip()} {family.strip()}" for family, given in pairs]


def gate_authors_agree() -> list[str]:
    """C. One author list, in one order, in all three places."""
    tex, readme, cff = _manuscript_authors(), _readme_authors(), _citation_authors()
    problems = []
    if not tex:
        problems.append("could not parse \\def\\Authors from the manuscript")
    for name, got in (("README.md", readme), ("CITATION.cff", cff)):
        if not got:
            problems.append(f"could not parse an author list from {name}")
        elif got != tex:
            problems.append(f"{name} author list differs from \\def\\Authors")
            problems.append(f"    manuscript: {tex}")
            problems.append(f"    {name:<13}: {got}")
    return problems


GATES = [
    ("A. every cited manuscript label resolves", gate_labels_resolve, True),
    ("B. no numbered manuscript references", gate_no_numbered_refs, True),
    ("C. author list identical in all three places", gate_authors_agree, False),
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--quiet", action="store_true", help="report failures only")
    args = ap.parse_args()

    files = repo_files()
    failed = 0
    print("=" * 70)
    print(f" check_repo.py -- {len(files)} repository files scanned")
    print("=" * 70)
    for title, fn, needs_files in GATES:
        problems = fn(files) if needs_files else fn()
        if problems:
            failed += 1
            print(f"\n  FAIL  {title}  ({len(problems)} problem(s))")
            for line in problems[:40]:
                print(f"          {line}")
            if len(problems) > 40:
                print(f"          ... and {len(problems) - 40} more")
        elif not args.quiet:
            print(f"\n  PASS  {title}")

    print("\n" + "=" * 70)
    print(f" {len(GATES) - failed} passed   {failed} failed")
    print("=" * 70)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
