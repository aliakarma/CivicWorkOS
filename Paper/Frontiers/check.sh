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
  n=$(grep -c 'Overfull' "$log" || true)
  [[ "$n" == 0 ]] && gate 7 "$doc: no overfull boxes" pass \
                  || gate 7 "$doc: no overfull boxes" fail "$n boxes"
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

n=$(grep -c 'keyword' "$MAIN.tex" || true)
(( n >= 1 )) && gate 5 "keywords declared" pass \
             || gate 5 "keywords declared" fail "none found"

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

grep -qE '\\correspondance\{[^}]' "$MAIN.tex" \
  && gate 5 "corresponding-author block passed" pass \
  || gate 5 "corresponding-author block passed" fail "\\correspondance{} empty"

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
