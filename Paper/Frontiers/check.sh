#!/usr/bin/env bash
# check.sh -- pre-submission gates for the Frontiers in Neurorobotics version.
#
#   ./check.sh             # build both documents, then run every gate
#   ./check.sh --no-build  # reuse the existing logs
#
# Run it, together with audit_numbers.py, before every submission build.
# Exit status is the number of failed gates (0 = ready).

set -uo pipefail
cd "$(dirname "$0")"

MAIN=CivicWorkOS
SUPP=CivicWorkOS_supplementary
WORD_CEILING=12000     # Frontiers Methods article limit
ABSTRACT_CEILING=350   # Frontiers abstract limit
REPO=../..

DO_BUILD=1
for arg in "$@"; do
  case "$arg" in
    --no-build) DO_BUILD=0 ;;
    *) echo "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

pass=0; fail=0
FAILED_GATES=()
gate() {
  local name=$1 result=$2 detail=${3:-}
  local label
  printf -v label '%-52s' "$name"
  if [[ "$result" == pass ]]; then
    pass=$((pass+1)); printf '  +  PASS  %s %s\n' "$label" "$detail"
  else
    fail=$((fail+1)); FAILED_GATES+=("$name")
    printf '  X  FAIL  %s %s\n' "$label" "$detail"
  fi
}

echo "======================================================================"
echo " CivicWorkOS -- Frontiers in Neurorobotics submission gates"
echo "======================================================================"

echo; echo "Build"
if (( DO_BUILD )); then
  for doc in $SUPP $MAIN; do
    latexmk -pdf -interaction=nonstopmode "$doc" > /dev/null 2>&1 || true
  done
  for doc in $MAIN $SUPP; do
    if latexmk -pdf -interaction=nonstopmode -halt-on-error "$doc" > "build-$doc.out" 2>&1; then
      gate "$doc builds" pass
    else
      gate "$doc builds" fail "see build-$doc.out"
    fi
  done
else
  echo "  (skipped; reusing existing logs)"
fi

for doc in $MAIN $SUPP; do
  log="$doc.log"
  [[ -f $log ]] || { gate "$doc log present" fail "no $log"; continue; }
  n=$(grep -cE 'Reference .* undefined|Citation .* undefined' "$log" || true)
  [[ "$n" == 0 ]] && gate "$doc: no undefined refs/citations" pass || gate "$doc: no undefined refs/citations" fail "$n hits"
  # The Frontiers classes emit one small \vbox overfull per page from the running
  # foot and an 8.5pt \hbox at \maketitle; those reproduce on an empty document.
  total=$(grep -c 'Overfull' "$log" || true)
  tmpl=$(grep -cE 'Overfull \\vbox \([0-2]\.[0-9]+pt too high\) has occurred while \\output is active|Overfull \\hbox \(8\.53581pt too wide\)' "$log" || true)
  n=$((total - tmpl))
  (( n <= 0 )) && gate "$doc: no overfull boxes" pass "($tmpl from the class)" \
               || gate "$doc: no overfull boxes" fail "$n boxes (+$tmpl from the class)"
done

echo; echo "Front matter and length"
basis=$(python -I count_words.py "$MAIN.tex" 2>/dev/null)
decl_w=$(grep -oE 'Word count:\} *[0-9,]+' "$MAIN.tex" | tr -dc '0-9')
(( ${basis:-99999} <= WORD_CEILING )) && gate "body words <= $WORD_CEILING" pass "$basis" \
                                      || gate "body words <= $WORD_CEILING" fail "$basis"
[[ -n "$basis" && "$basis" == "$decl_w" ]] && gate "declared word count matches journal basis" pass "$basis" \
  || gate "declared word count matches journal basis" fail "declared ${decl_w:-none}, measured ${basis:-?}"

abs_words=$(python -I - "$MAIN.tex" <<'PY'
import re, sys
s = open(sys.argv[1], encoding="utf-8").read()
a = s[s.index("\\begin{abstract}") + 16:s.index("\\tiny", s.index("\\begin{abstract}"))]
a = re.sub(r"\\[a-zA-Z]+", " ", a)
print(len(a.split()))
PY
)
(( abs_words <= ABSTRACT_CEILING )) && gate "abstract <= $ABSTRACT_CEILING words" pass "$abs_words" \
                                   || gate "abstract <= $ABSTRACT_CEILING words" fail "$abs_words"

kw=$(grep -oE '\\section\{Keywords:\}[^}]*' "$MAIN.tex" | head -1 | sed 's/.*Keywords:}//')
n=0; [[ -n "${kw// /}" ]] && n=$(echo "$kw" | awk -F, '{print NF}')
(( n >= 5 && n <= 8 )) && gate "keywords declared (5-8)" pass "$n" || gate "keywords declared (5-8)" fail "$n found"

nfig=$(grep -c 'begin{figure}' "$MAIN.tex")
decl_f=$(grep -oE 'Number of figures:\} *[0-9]+' "$MAIN.tex" | tr -dc '0-9')
[[ "$nfig" == "$decl_f" ]] && gate "declared figure count matches" pass "$nfig" \
                           || gate "declared figure count matches" fail "declared $decl_f, found $nfig"
ntab=$(grep -c 'begin{table}' "$MAIN.tex")
decl_t=$(grep -oE 'Number of tables:\} *[0-9]+' "$MAIN.tex" | tr -dc '0-9')
[[ "$ntab" == "$decl_t" ]] && gate "declared table count matches" pass "$ntab" \
                           || gate "declared table count matches" fail "declared $decl_t, found $ntab"

grep -q 'Article type:} Methods' "$MAIN.tex" && gate "article type declared (Methods)" pass || gate "article type declared (Methods)" fail
grep -q 'Research Topic:' "$MAIN.tex" && gate "Research Topic declared" pass || gate "Research Topic declared" fail

hits=$(grep -nE 'WORDCOUNT|WALLTIME|SIMRESULTS|EXTRESULTS|DISCUSSION$|CONCLUSIONS$|TODO|TBD|XXXX|FIXME' "$MAIN.tex" "$SUPP.tex" || true)
[[ -z "$hits" ]] && gate "no placeholders" pass || gate "no placeholders" fail "$(echo "$hits" | wc -l | tr -d ' ') hits"

for sec in 'Ethics Statement' 'Data Availability Statement' 'Author Contributions' 'Funding' 'Conflict of Interest' 'Generative AI Statement'; do
  grep -q "section\*{$sec}" "$MAIN.tex" && gate "$sec present" pass || gate "$sec present" fail
done

hits=$(grep -n 'includegraphics' "$MAIN.tex" "$SUPP.tex" || true)
[[ -z "$hits" ]] && gate "all figures vector (no raster includes)" pass || gate "all figures vector (no raster includes)" fail "$(echo "$hits" | wc -l | tr -d ' ') includes"

if [[ -f cover-letter.md ]]; then
  words=$(echo "$decl_w" | sed -E ':a;s/([0-9])([0-9]{3})($|,)/\1,\2\3/;ta')
  want="$words words, with $decl_f figures and $decl_t tables"
  grep -q "$want" cover-letter.md && gate "cover letter counts match front matter" pass \
                                  || gate "cover letter counts match front matter" fail "expected \"$want\""
else
  gate "cover letter counts match front matter" fail "cover-letter.md missing"
fi

echo; echo "Language and bibliography"
hits=$(grep -nE '\\cite\{' "$MAIN.tex" "$SUPP.tex" || true)
[[ -z "$hits" ]] && gate "no bare \\cite (use \\citet/\\citep)" pass || gate "no bare \\cite (use \\citet/\\citep)" fail "$(echo "$hits" | wc -l | tr -d ' ') hits"
hits=$(grep -nE '\b(behaviour|modell(ed|ing)|labell(ed|ing)|centre|programme|catalogue|whilst|amongst|judgement|optimis|minimis|maximis|normalis|recognis|organis(e|ed|ing|ation)|summaris|characteris|emphasis(e|ed))' "$MAIN.tex" "$SUPP.tex" | grep -v 'Labour Organization' || true)
[[ -z "$hits" ]] && gate "US orthography" pass || gate "US orthography" fail "$(echo "$hits" | wc -l | tr -d ' ') hits"
nhits=$(python -I - "$MAIN.tex" "$SUPP.tex" <<'PY'
import re, sys
n = 0
for path in sys.argv[1:]:
    for line in open(path, encoding="utf-8"):
        s = line.strip()
        if s.startswith("%"):
            continue
        # a "---" alone in a table cell marks an empty cell, not a dash in prose
        s = re.sub(r"(^|&)\s*---\s*(?=&|\\\\|$)", r"\1", s)
        if "—" in s or "---" in s:
            n += 1
print(n)
PY
)
[[ "$nhits" == 0 ]] && gate "no em dashes in prose" pass || gate "no em dashes in prose" fail "$nhits lines"

echo; echo "Numbers, data and software"
if python -I audit_numbers.py --quiet > audit.out 2>&1; then
  gate "audit_numbers.py" pass "$(grep -o '[0-9]* PASS' audit.out | head -1)"
else
  gate "audit_numbers.py" fail "see audit.out"
fi
cp "$MAIN.tex" /tmp/_main_before.tex; cp "$SUPP.tex" /tmp/_supp_before.tex
python -I make_sim_tables.py --splice > /dev/null 2>&1
if cmp -s "$MAIN.tex" /tmp/_main_before.tex && cmp -s "$SUPP.tex" /tmp/_supp_before.tex; then
  gate "generated tables and Figure 4 in sync with data/" pass
else
  gate "generated tables and Figure 4 in sync with data/" fail "re-spliced; rebuild the PDFs"
fi
[[ -f data/summary.json && -f data/hypotheses.json && -f data/exploratory.json ]] \
  && gate "data/ summaries present" pass || gate "data/ summaries present" fail
grep -q '"DEVIATIONS": \[\]\|DEVIATIONS: \[\]' $REPO/configs/protocol/hypotheses.yaml \
  && gate "pre-specified hypotheses: no undeclared deviations" pass || gate "pre-specified hypotheses: no undeclared deviations" fail "check DEVIATIONS"

if (cd $REPO && python -I scripts/verify_worked_example.py) > verify.out 2>&1; then
  gate "verify_worked_example.py" pass
else
  gate "verify_worked_example.py" fail "see verify.out"
fi
if (cd $REPO && python -I -m pytest -q) > pytest.out 2>&1; then
  n=$(grep -oE '[0-9]+ passed' pytest.out | head -1 | tr -dc '0-9')
  badge=$(grep -oE 'Tests-[0-9]+' $REPO/README.md | head -1 | tr -dc '0-9')
  [[ "$n" == "$badge" ]] && gate "pytest passes and matches README badge" pass "$n passed" \
                         || gate "pytest passes and matches README badge" fail "suite $n, badge ${badge:-absent}"
else
  gate "pytest passes and matches README badge" fail "see pytest.out"
fi

echo
echo "======================================================================"
echo " $pass passed, $fail failed"
(( fail )) && printf '   - %s\n' "${FAILED_GATES[@]}"
echo "======================================================================"
exit $fail
