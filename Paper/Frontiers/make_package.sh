#!/usr/bin/env bash
# make_package.sh -- assemble the Frontiers submission package (Phase 8, item 7).
#
# Copies exactly the files the two documents need into submission/, builds
# both there from nothing to prove the package is self-contained, and zips
# the sources. Build products stay out of the zip except the .bbl files,
# which Frontiers' production system uses when it re-typesets.
#
#   ./make_package.sh

set -euo pipefail
cd "$(dirname "$0")"

OUT=submission
rm -rf "$OUT" CivicWorkOS-submission.zip
mkdir -p "$OUT/images"

SOURCES=(
  CivicWorkOS.tex
  CivicWorkOS_supplementary.tex
  references.bib
  FrontiersinHarvard.cls
  frontiers_suppmat.cls
  Frontiers-Harvard.bst
  logo1.eps
  images/arch.png
  images/runtime.png
)
DOCS=(
  cover-letter.md
  response-to-reviewers.md
  CivicWorkOS-diff.pdf
)

for f in "${SOURCES[@]}" "${DOCS[@]}"; do
  [[ -f "$f" ]] || { echo "missing: $f" >&2; exit 1; }
  cp "$f" "$OUT/$f"
done

# Build from a clean directory. The documents cross-reference each other
# through xr, so warm both up before the reported pass.
(
  cd "$OUT"
  for doc in CivicWorkOS_supplementary CivicWorkOS; do
    latexmk -pdf -interaction=nonstopmode "$doc" > /dev/null 2>&1 || true
  done
  for doc in CivicWorkOS CivicWorkOS_supplementary; do
    latexmk -pdf -interaction=nonstopmode -halt-on-error "$doc" > "build-$doc.out" 2>&1 \
      || { echo "$doc does not build from the package; see $OUT/build-$doc.out" >&2; exit 1; }
    if grep -qi 'undefined' "$doc.log"; then
      echo "$doc has undefined references when built from the package" >&2; exit 1
    fi
  done
)

# Zip the sources, the .bbl files and the two PDFs; leave other build products out.
(
  cd "$OUT"
  python -I -c 'import sys, zipfile; z = zipfile.ZipFile(sys.argv[1], "w", zipfile.ZIP_DEFLATED); [z.write(p) for p in sys.argv[2:]]; z.close()'     ../CivicWorkOS-submission.zip "${SOURCES[@]}" "${DOCS[@]}"     CivicWorkOS.bbl CivicWorkOS_supplementary.bbl     CivicWorkOS.pdf CivicWorkOS_supplementary.pdf
)

echo "package: $OUT/ and CivicWorkOS-submission.zip"
python -I -c "import sys, zipfile; [print(str(i.file_size).rjust(10), i.filename) for i in zipfile.ZipFile(sys.argv[1]).infolist()]" CivicWorkOS-submission.zip
