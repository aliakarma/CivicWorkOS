#!/usr/bin/env bash
# check.sh -- build and compliance gates for the CivicWorkOS Frontiers revision.
#
# Each gate is tagged with the phase of REVISION-PROGRAMME.md that closes it.
# Gates whose phase is at or below the phase passed on the command line are
# enforced; later gates are reported as PENDING and do not fail the run. This
# keeps the script useful from Phase 0 onward instead of being a wall of red
# until the last day.
#
#   ./check.sh            # enforce gates up to the phase in .revision-phase
#   ./check.sh 1          # enforce gates closed by Phase 1 and earlier
#   ./check.sh --all      # enforce every gate (the pre-submission run)
#   ./check.sh --no-build # skip the LaTeX build, reuse the existing log
#
# Run it, together with audit_numbers.py, at the end of every working session.

set -uo pipefail
cd "$(dirname "$0")"

MAIN=CivicWorkOS
SUPP=CivicWorkOS_supplementary
PHASE_FILE=.revision-phase
WORD_CEILING=11800     # Phase 4 target, with margin under the 12,000 limit

DO_BUILD=1
PHASE=""
for arg in "$@"; do
  case "$arg" in
    --all)      PHASE=99 ;;
    --no-build) DO_BUILD=0 ;;
    [0-9]*)     PHASE="$arg" ;;
    *) echo "unknown argument: $arg" >&2; exit 2 ;;
  esac
done
if [[ -z "$PHASE" ]]; then
  PHASE=$( [[ -f $PHASE_FILE ]] && tr -dc '0-9' < $PHASE_FILE || echo 0 )
  PHASE=${PHASE:-0}
fi

pass=0; fail=0; pending=0
FAILED_GATES=()

# gate <phase-that-closes-it> <name> <pass|fail> [detail]
gate() {
  local p=$1 name=$2 result=$3 detail=${4:-}
  local label
  printf -v label '%-46s' "$name"
  if [[ "$result" == pass ]]; then
    pass=$((pass+1)); printf '  +  PASS     %s %s\n' "$label" "$detail"
  elif (( p > PHASE )); then
    pending=$((pending+1))
    printf '  .  PENDING  %s %s  (closes in Phase %s)\n' "$label" "$detail" "$p"
  else
    fail=$((fail+1)); FAILED_GATES+=("$name")
    printf '  X  FAIL     %s %s  (Phase %s)\n' "$label" "$detail" "$p"
  fi
}

echo "======================================================================"
echo " CivicWorkOS submission gates -- enforcing through Phase $PHASE"
echo "======================================================================"

# ---------------------------------------------------------------- build ----
echo
echo "Build"
if (( DO_BUILD )); then
  # The two documents cross-reference each other through xr, so on a clean
  # tree each needs the other's .aux before its references can resolve. A
  # silent warm-up pass of both makes the reported pass below converge.
  for doc in $SUPP $MAIN; do
    latexmk -pdf -interaction=nonstopmode "$doc" > /dev/null 2>&1 || true
  done
  for doc in $MAIN $SUPP; do
    if latexmk -pdf -interaction=nonstopmode -halt-on-error "$doc" \
         > "/tmp/latexmk-$doc.out" 2>&1; then
      gate 0 "$doc builds" pass
    else
      gate 0 "$doc builds" fail "see /tmp/latexmk-$doc.out"
    fi
  done
else
  echo "  (skipped; reusing existing logs)"
fi

for doc in $MAIN $SUPP; do
  log="$doc.log"
  if [[ ! -f $log ]]; then
    gate 0 "$doc log present" fail "no $log"
    continue
  fi
  n=$(grep -ci 'undefined' "$log" || true)
  [[ "$n" == 0 ]] && gate 1 "$doc: no undefined refs/citations" pass \
                  || gate 1 "$doc: no undefined refs/citations" fail "$n hits"
  # Two overfull warnings come from the Frontiers classes themselves and
  # reproduce in an empty document built on the unmodified class: the running
  # foot is a fixed-height \vbox a point or two shorter than its contents (one
  # warning per page, emitted by \output), and \maketitle sets an 8.5pt-wide
  # line. Production re-typesets with Frontiers' own class, so they are counted
  # separately; any other overfull box -- including a large one in \output,
  # which is how an oversized float shows up -- fails the gate.
  # TeX reports the \maketitle line, or the next one when a blank line ends it.
  mt=$(grep -n '^[[:space:]]*\\maketitle' "$doc.tex" | head -1 | cut -d: -f1)
  mt=${mt:-0}; mt1=$((mt + 1))
  TEMPLATE_OVERFULL="Overfull \\\\vbox \\([0-2]\\.[0-9]+pt too high\\) has occurred while \\\\output is active|Overfull \\\\hbox \\(8\\.53581pt too wide\\) in paragraph at lines ($mt--$mt|$mt1--$mt1)\$"
  total=$(grep -c 'Overfull' "$log" || true)
  tmpl=$(grep -cE "$TEMPLATE_OVERFULL" "$log" || true)
  n=$((total - tmpl))
  [[ "$n" == 0 ]] && gate 7 "$doc: no overfull boxes" pass "($tmpl from the class)" \
                  || gate 7 "$doc: no overfull boxes" fail \
                       "$n boxes (+$tmpl from the class)"
done

pages=$(grep -o 'Output written.*(\([0-9]*\) pages' "$MAIN.log" 2>/dev/null \
        | grep -o '([0-9]* pages' | tr -dc '0-9' || true)
[[ -n "${pages:-}" ]] && echo "     page count: $pages"

# --------------------------------------------------------------- length ----
echo
echo "Length and front matter"
words=$(texcount -inc -total -q "$MAIN.tex" 2>/dev/null \
        | grep -i 'Words in text' | tr -dc '0-9' || true)
words=${words:-0}
if (( words <= WORD_CEILING )); then
  gate 4 "body words <= $WORD_CEILING" pass "$words"
else
  gate 4 "body words <= $WORD_CEILING" fail "$words"
fi

# Frontiers requires 5 to 8 keywords, set as \section{Keywords:} a, b, ...
kw=$(grep -oE '\\section\{Keywords:\}[^}]*' "$MAIN.tex" | head -1 \
     | sed 's/.*Keywords:}//')
n=0; [[ -n "${kw// /}" ]] && n=$(echo "$kw" | awk -F, '{print NF}')
(( n >= 5 && n <= 8 )) && gate 5 "keywords declared (5-8)" pass "$n" \
                       || gate 5 "keywords declared (5-8)" fail "$n found"

hits=$(grep -nE '26UQU\(|\(Staff number\)|\(track name\)|TODO|TBD|XXXX|FIXME' \
       "$MAIN.tex" || true)
[[ -z "$hits" ]] && gate 5 "no placeholders" pass \
                 || gate 5 "no placeholders" fail \
                      "$(echo "$hits" | wc -l | tr -d ' ') hits"

grep -q 'Ethics Statement' "$MAIN.tex" \
  && gate 5 "Ethics Statement present" pass \
  || gate 5 "Ethics Statement present" fail

if grep -qE '\\section\*?\{Abbreviations\}' "$MAIN.tex"; then
  body=$(sed -n '/section\*{Abbreviations}/,/section\*{/p' "$MAIN.tex" \
         | sed '1d;$d' | tr -d '[:space:]')
  [[ -n "$body" ]] && gate 5 "Abbreviations populated or absent" pass \
                   || gate 5 "Abbreviations populated or absent" fail "present but empty"
else
  gate 5 "Abbreviations populated or absent" pass "absent"
fi

# The class prints \corrAuthor and \corrEmail after \correspondance{}, which
# the Frontiers template leaves empty; filling it would print the name twice.
# So check that both are defined and that the block reaches the PDF.
cauth=$(sed -n 's/^\\def\\corrAuthor{\(.*\)}$/\1/p' "$MAIN.tex")
cmail=$(sed -n 's/^\\def\\corrEmail{\(.*\)}$/\1/p' "$MAIN.tex")
if [[ -n "$cauth" && -n "$cmail" ]] && command -v pdftotext > /dev/null \
   && pdftotext -f 1 -l 1 "$MAIN.pdf" - 2>/dev/null \
      | tr '\n' ' ' | grep -q "Correspondence\*: *$cauth *$cmail"; then
  gate 5 "corresponding-author block renders" pass "$cmail"
else
  gate 5 "corresponding-author block renders" fail "not on page 1"
fi

# L5: an equal-contribution footnote needs a dagger on at least two authors.
if grep -q 'contributed equally' "$MAIN.tex"; then
  nd=$(sed -n '/\\def\\Authors{/,/^}/p' "$MAIN.tex" | grep -c 'dagger')
  (( nd >= 2 )) && gate 5 "equal-contribution footnote attached" pass \
                || gate 5 "equal-contribution footnote attached" fail \
                     "$nd authors marked"
else
  gate 5 "equal-contribution footnote attached" pass "absent"
fi

# L7: every initial in Author Contributions must name exactly one author.
contrib=$(sed -n '/section\*{Author Contributions}/,/section\*{Funding}/p' \
          "$MAIN.tex")
if echo "$contrib" | grep -qE '\bAA\b'; then
  gate 5 "author initials unambiguous" fail "AA names two authors"
else
  gate 5 "author initials unambiguous" pass
fi

# ------------------------------------------------------------ integrity ----
echo
echo "Integrity (Phase 1)"

DELETED_LABELS='tab:mainresults|tab:persector|tab:ablation|tab:stress|tab:runtime|tab:hypoutcomes|sec:results|sec:status|sec:mainresults|sec:persector|sec:ablation|sec:stressresults|sec:retirement|sec:distresults|sec:runtime|sec:hypoutcomes|sec:expsetup|sec:testbed|sec:baselines|sec:metrics|sec:config|sec:statplan|sec:predictions|tab:sectors|tab:params|tab:predictions'
hits=$(grep -nE "ref\{($DELETED_LABELS)\}" "$MAIN.tex" "$SUPP.tex" || true)
[[ -z "$hits" ]] && gate 1 "no refs to deleted Section 8 labels" pass \
                 || gate 1 "no refs to deleted Section 8 labels" fail \
                      "$(echo "$hits" | wc -l | tr -d ' ') hits"

FABRICATED='63\.2%|86\.8|0\.942|52\.9|thirty paired|simulated dual|was not refuted|were not refuted|0\.97.{0,20}Capability-Formation|Capability-Formation Index of 0\.97'
hits=$(grep -nE "$FABRICATED" "$MAIN.tex" || true)
[[ -z "$hits" ]] && gate 1 "no fabricated Section 8 figures" pass \
                 || gate 1 "no fabricated Section 8 figures" fail \
                      "$(echo "$hits" | wc -l | tr -d ' ') hits"

RESULTS_TENSE='\b(CivicWorkOS (achieved|attained|exhibited)|No strategy dominated|was observed|were observed|we measured|the simulation (shows|showed|reports|reported|confirms)|reproducing the analytical|the simulated|across thirty)\b'
hits=$(grep -nEi "$RESULTS_TENSE" "$MAIN.tex" || true)
[[ -z "$hits" ]] && gate 1 "no past-tense results language" pass \
                 || gate 1 "no past-tense results language" fail \
                      "$(echo "$hits" | wc -l | tr -d ' ') hits"

grep -q 'has not been executed' "$MAIN.tex" \
  && gate 1 "protocol declared unexecuted" pass \
  || gate 1 "protocol declared unexecuted" fail

grep -qi 'Hypothesis and Theory' "$MAIN.tex" \
  && gate 1 "article type declared" pass \
  || gate 1 "article type declared" fail

# ------------------------------------------------ numerical consistency ----
echo
echo "Numerical consistency (Phase 2)"

# M1: one capability price, quoted consistently.  0.0455 is the value the
# rounded intermediate used to imply; it must appear nowhere.
hits=$(grep -nE '0\.0455' "$MAIN.tex" "$SUPP.tex" || true)
[[ -z "$hits" ]] && gate 2 "single capability price (no 0.0455)" pass \
                 || gate 2 "single capability price (no 0.0455)" fail \
                      "$(echo "$hits" | wc -l | tr -d ' ') hits"

# M1: the equation must carry the unrounded numerator that reproduces it.
grep -q '0.027212' "$MAIN.tex" \
  && gate 2 "eq:lambdaworked reproduces its own quotient" pass \
  || gate 2 "eq:lambdaworked reproduces its own quotient" fail \
       "six-decimal numerator absent"

# H5: the overstated robustness claim must not come back.
hits=$(grep -nE 'every feasible value|does not depend on the estimates' \
       "$MAIN.tex" "$SUPP.tex" || true)
[[ -z "$hits" ]] && gate 2 "no overstated robustness claim" pass \
                 || gate 2 "no overstated robustness claim" fail \
                      "$(echo "$hits" | wc -l | tr -d ' ') hits"

# M3: the superseded debt-trajectory constants.
STALE_CAD='ceiling of 13\.5|at 1\.37 units|t=9\.34|\$t=9\.34\$|year 9\.34'
hits=$(grep -nE "$STALE_CAD" "$MAIN.tex" "$SUPP.tex" || true)
[[ -z "$hits" ]] && gate 2 "no superseded debt-trajectory constants" pass \
                 || gate 2 "no superseded debt-trajectory constants" fail \
                      "$(echo "$hits" | wc -l | tr -d ' ') hits"

# M3: the figure is only reproducible if its parameters are tabulated.
grep -q 'label{tab:cadparams}' "$MAIN.tex" \
  && gate 2 "fig:cad-trend parameters tabulated" pass \
  || gate 2 "fig:cad-trend parameters tabulated" fail "tab:cadparams absent"

# ------------------------------------------------ substantive additions ----
echo
echo "Substantive strengthening (Phase 6)"

# Prints the body of one \section/\subsection, from its heading to the next.
sec_body() {
  awk -v lbl="$1" '
    /\\(sub)?section\*?\{/ { if (on && seen) exit }
    index($0, "label{" lbl "}") { on = 1; seen = 1 }
    on' "$MAIN.tex"
}

# L8: the intake requirement in the Abstract, the Contributions, a figure,
# sec:pipeline, and the Conclusions.
missing=()
sed -n '/begin{abstract}/,/end{abstract}/p' "$MAIN.tex" \
  | grep -q 'fourteen are required' || missing+=(abstract)
sed -n '/label{sec:contributions}/,/end{itemize}/p' "$MAIN.tex" \
  | grep -q 'capability intake requirement' || missing+=(contributions)
grep -q 'label{fig:intake}' "$MAIN.tex" || missing+=(figure)
sec_body sec:pipeline | grep -q 'ref{fig:intake}' || missing+=(sec:pipeline)
sec_body sec:conclusion | grep -q 'ref{fig:intake}' || missing+=(conclusions)
(( ${#missing[@]} == 0 )) \
  && gate 6 "intake requirement promoted (L8)" pass \
  || gate 6 "intake requirement promoted (L8)" fail "missing: ${missing[*]}"

# M7: a GCC subsection that names a composition instrument and connects
# ILOESCWA2026 to the Just Transition Constraint.
gcc=$(sec_body sec:gcc)
if [[ -n "$gcc" ]] && grep -q 'Nitaqat' <<< "$gcc" \
   && grep -q 'ILOESCWA2026' <<< "$gcc" \
   && grep -q 'eq:justtransition' <<< "$gcc"; then
  gate 6 "GCC subsection present and connected (M7)" pass
else
  gate 6 "GCC subsection present and connected (M7)" fail
fi

# M8: the online-rule discussion states a bound, cites both literatures,
# and the Limitations bullet points at it.
ob=$(sec_body sec:onlinebound)
n=$(grep -oE 'First,|Second,|Third,|Fourth,' <<< "$ob" | wc -l)
if grep -q 'regret' <<< "$ob" && grep -q 'Altman1999' <<< "$ob" \
   && grep -qE 'Mehta2007|DevanurHayes2009|Balseiro2023' <<< "$ob" \
   && (( n >= 3 )) \
   && sec_body sec:limitations | grep -q 'ref{sec:onlinebound}'; then
  gate 6 "online-rule bound engaged (M8)" pass "$n obstacles"
else
  gate 6 "online-rule bound engaged (M8)" fail
fi

# M6: the convex-hull limit sits where the legitimacy claim is made, and the
# Limitations section points at it instead of restating it.
if sec_body sec:feedback | grep -q 'convex hull' \
   && ! sec_body sec:limitations | grep -q 'aggregation function' \
   && sec_body sec:limitations | grep -q 'ref{sec:feedback}'; then
  gate 6 "scalarization limit in sec:feedback (M6)" pass
else
  gate 6 "scalarization limit in sec:feedback (M6)" fail
fi

# \extraAuth must keep pace with the figure count.
nfig=$(grep -c 'begin{figure}' "$MAIN.tex")
decl=$(grep -oE 'Number of figures:\} *[0-9]+' "$MAIN.tex" | tr -dc '0-9')
[[ "$nfig" == "$decl" ]] \
  && gate 6 "declared figure count matches" pass "$nfig" \
  || gate 6 "declared figure count matches" fail "declared $decl, found $nfig"

# ------------------------------------------------ language and citations ----
echo
echo "Language and bibliography (Phase 7)"

# N5: natbib's \cite is textual, so "Author~\cite{k}" printed the authors
# twice and an aside printed unbracketed. Use \citet or \citep, never \cite.
hits=$(grep -nE '\\cite\{' "$MAIN.tex" "$SUPP.tex" || true)
[[ -z "$hits" ]] && gate 7 "no bare \\cite (use \\citet/\\citep) (N5)" pass \
                 || gate 7 "no bare \\cite (use \\citet/\\citep) (N5)" fail \
                      "$(echo "$hits" | wc -l | tr -d ' ') hits"

# L2: US orthography. "International Labour Organization" is a proper name.
UK='\b(behaviou?r(al|ally|s)?|[a-z]*our(able|ably|ed|ing|ite)\b|modell(ed|ing)|labell(ed|ing)|travell(ed|ing)|cancell(ed|ing)|signall(ed|ing)|centre|programme|catalogue|analys(e|ed|ing)|whilst|amongst|judgement|[a-z]+is(ation|ations|ed|es|ing)\b)'
hits=$(grep -nE "$UK" "$MAIN.tex" "$SUPP.tex" | grep -iE 'behaviour|our(able|ably|ed|ing|ite)|modell|labell|travell|cancell|signall|centre|programme|catalogue|analys(e|ed|ing)\b|whilst|amongst|judgement|(organ|real|util|optim|minim|maxim|normal|recogn|author|categor|character|emphas|summar|prior|standard|operational|special|general|central|formal|parameter|regular|visual|stabil|initial|penal|legal|digit)is(ation|ed|es|ing)\b' \
       | grep -v 'Labour Organization' || true)
[[ -z "$hits" ]] && gate 7 "US orthography (L2)" pass \
                 || gate 7 "US orthography (L2)" fail \
                      "$(echo "$hits" | wc -l | tr -d ' ') hits"

# M9: syed2026fedagent does not support the algorithmic-management claim.
hits=$(grep -nE 'syed2026fedagent' "$MAIN.tex" "$SUPP.tex" || true)
[[ -z "$hits" ]] && gate 7 "syed2026fedagent not misapplied (M9)" pass \
                 || gate 7 "syed2026fedagent not misapplied (M9)" fail \
                      "re-sited? check it supports the claim"

# -------------------------------------------------------------- numbers ----
echo
echo "Arithmetic and artifact"
if python -I audit_numbers.py --quiet > /tmp/audit.out 2>&1; then
  gate 0 "audit_numbers.py" pass "$(grep -o '[0-9]* PASS' /tmp/audit.out | head -1)"
else
  gate 0 "audit_numbers.py" fail "see /tmp/audit.out"
fi

REPO=../..
if [[ -f $REPO/scripts/verify_worked_example.py ]]; then
  if (cd $REPO && python -I scripts/verify_worked_example.py) \
       > /tmp/verify.out 2>&1; then
    gate 3 "verify_worked_example.py" pass
  else
    gate 3 "verify_worked_example.py" fail "see /tmp/verify.out"
  fi
else
  gate 3 "verify_worked_example.py" fail "script not found"
fi

# Phase 3 reconciliation: labels resolve, no numbered references survive, and
# one author list in three places. Scoped to the whole repository, not just
# README/scripts/sim, because src/ and tests/ carried the same stale numbering.
if python -I check_repo.py --quiet > /tmp/check_repo.out 2>&1; then
  gate 3 "repo/manuscript reconciliation" pass
else
  gate 3 "repo/manuscript reconciliation" fail "see /tmp/check_repo.out"
fi

# The README advertises a test count; it has to be true. Finding N3 was that
# the advertised suite did not run at all on a clean environment.
if (cd $REPO && python -I -m pytest -q) > /tmp/pytest.out 2>&1; then
  n=$(grep -oE '[0-9]+ passed' /tmp/pytest.out | head -1 | tr -dc '0-9')
  badge=$(grep -oE 'Tests-[0-9]+' $REPO/README.md | head -1 | tr -dc '0-9')
  if [[ "$n" == "$badge" ]]; then
    gate 3 "pytest matches README badge" pass "$n passed"
  else
    gate 3 "pytest matches README badge" fail "suite $n, badge ${badge:-absent}"
  fi
else
  gate 3 "pytest matches README badge" fail "see /tmp/pytest.out"
fi

# ------------------------------------------------------ submission package ----
echo
echo "Submission package (Phase 8)"

# \extraAuth states the count on the journal's basis: texcount's text total
# less the abstract, acknowledgment and funding statement.
basis=$(python -I count_words.py "$MAIN.tex" 2>/dev/null)
decl_w=$(grep -oE 'Word count:\} *[0-9,]+' "$MAIN.tex" | tr -dc '0-9')
[[ -n "$basis" && "$basis" == "$decl_w" ]] \
  && gate 8 "declared word count matches journal basis" pass "$basis" \
  || gate 8 "declared word count matches journal basis" fail "declared $decl_w, measured ${basis:-?}"

ntab=$(grep -c 'begin{table}' "$MAIN.tex")
decl_t=$(grep -oE 'Number of tables:\} *[0-9]+' "$MAIN.tex" | tr -dc '0-9')
[[ "$ntab" == "$decl_t" ]] \
  && gate 8 "declared table count matches" pass "$ntab" \
  || gate 8 "declared table count matches" fail "declared $decl_t, found $ntab"

# The cover letter restates the counts; it drifted once already.
if [[ -f cover-letter.md ]]; then
  decl_f=$(grep -oE 'Number of figures:\} *[0-9]+' "$MAIN.tex" | tr -dc '0-9')
  words=$(echo "$decl_w" | sed -E ':a;s/([0-9])([0-9]{3})($|,)/\1,\2\3/;ta')
  want="$words words, with $decl_f figures and $decl_t tables"
  grep -q "$want" cover-letter.md \
    && gate 8 "cover letter counts match \\extraAuth" pass \
    || gate 8 "cover letter counts match \\extraAuth" fail "expected \"$want\""
else
  gate 8 "cover letter counts match \\extraAuth" fail "cover-letter.md missing"
fi

# One response entry per register ID in REVISION-PROGRAMME.md section 4.
if [[ -f response-to-reviewers.md ]]; then
  ids=$(grep -oE '^\| \*\*[CHMLN][0-9]+\*\*' REVISION-PROGRAMME.md | tr -dc 'A-Z0-9\n' | sort -u)
  missing=$(for id in $ids; do grep -qE "^\| $id \|" response-to-reviewers.md || echo "$id"; done | tr '\n' ' ')
  [[ -z "${missing// }" ]] \
    && gate 8 "response covers every register item" pass "$(echo "$ids" | wc -w | tr -d ' ') items" \
    || gate 8 "response covers every register item" fail "missing: $missing"
else
  gate 8 "response covers every register item" fail "response-to-reviewers.md missing"
fi

# N6: the Data Availability link names no branch, so readers land on the
# default branch. It must carry the revision, or N1-N4 are live again there.
main_sha=$(cd $REPO && git ls-remote origin refs/heads/main 2>/dev/null | cut -f1)
if [[ -z "$main_sha" ]]; then
  gate 8 "default branch carries the revision (N6)" fail "origin unreachable"
elif (cd $REPO && git merge-base --is-ancestor HEAD "$main_sha" 2>/dev/null); then
  gate 8 "default branch carries the revision (N6)" pass "${main_sha:0:7}"
else
  gate 8 "default branch carries the revision (N6)" fail "origin/main ${main_sha:0:7} lacks HEAD"
fi

# -------------------------------------------------- evidence upgrade (Phase 9) ----
echo
echo "Evidence upgrade (Phase 9a: elicitation readiness)"

# The elicitation pipeline's own tests: ICC against the published example, the
# re-solver against the printed sensitivity table, and the data guards.
if (cd $REPO && python -I -m pytest -q elicitation/tests -p no:cacheprovider) \
     > /tmp/elicit.out 2>&1; then
  gate 9 "elicitation pipeline tests" pass "$(grep -oE '[0-9]+ passed' /tmp/elicit.out)"
else
  gate 9 "elicitation pipeline tests" fail "see /tmp/elicit.out"
fi

# Nothing synthetic may reach either manuscript source. The synthetic outputs
# are also built to error a LaTeX run; this catches the \input before a build.
if grep -nE 'SYNTHETIC|elicitation/(out|fixtures)' "$MAIN.tex" "$SUPP.tex" > /tmp/syn.out; then
  gate 9 "no synthetic elicitation output in the manuscript" fail "$(head -1 /tmp/syn.out)"
else
  gate 9 "no synthetic elicitation output in the manuscript" pass
fi

# The manuscript's claim about the protocol must match the evidence on disk.
# No real results file: the Limitations bullet must still say the protocol has
# not been run. A real results file: the bullet must have been revised.
real_results=$(ls $REPO/elicitation/out/results.json 2>/dev/null)
claims_unrun=$(grep -c 'has not been run' "$MAIN.tex")
if [[ -z "$real_results" ]]; then
  (( claims_unrun >= 1 )) \
    && gate 9 "elicitation claim matches the evidence" pass "no real data; manuscript says not run" \
    || gate 9 "elicitation claim matches the evidence" fail "no real data, yet 'has not been run' is gone"
else
  (( claims_unrun == 0 )) \
    && gate 9 "elicitation claim matches the evidence" pass "real results present; bullet revised" \
    || gate 9 "elicitation claim matches the evidence" fail "real results exist; 'has not been run' still printed"
fi

# ------------------------------------------------------------- summary ----
echo
echo "======================================================================"
printf ' %d passed   %d failed   %d pending\n' "$pass" "$fail" "$pending"
if (( fail )); then
  echo
  echo ' Failing gates:'
  for g in "${FAILED_GATES[@]}"; do echo "   - $g"; done
fi
echo "======================================================================"
exit $(( fail > 0 ? 1 : 0 ))
