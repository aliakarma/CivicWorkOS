# Ratings file format

One CSV, long format, one rating per row. The first lines are header comments:

```
# provenance: real
# ethics-approval: <reference issued by the approving committee>
rater_id,group,round,parameter,item_id,value,rationale
```

`analyze.py` refuses the file without `provenance`, and refuses `provenance: real`
without `ethics-approval`. `provenance: synthetic` is refused unless
`--allow-synthetic` is passed, and then every output is watermarked.

| Column | Values |
|---|---|
| `rater_id` | pseudonym, e.g. `R01`. No names, no employer. |
| `group` | `competent`, `developing`, `supervisor` (App. S4 participants; equal numbers) |
| `round` | `1` independent, `2` after the anonymised round-one distribution |
| `parameter` | `learn`, `phi`, `psi_ratio`, `h_raw_doc`, `h_raw_prac` |
| `item_id` | `learn`: task id (`T01`..`T12`). `phi`: `<mode>\|<task id>` with mode in `H+A`, `H+R`, `H+A+R`. `psi_ratio`: class id (`C1`..`C4`). `h_raw_*`: `R1` |
| `value` | `learn`, `phi`: 0..10 on the anchored scale. `psi_ratio`: developing practitioners per competent lead (>= 0). `h_raw_*`: supervised clock hours (> 0) |
| `rationale` | free text, required in round 1 for ratings at either end of the scale |

`phi_H` is 1 by definition (the human forms the determination) and is not elicited.
Item texts are in `items.csv`; anchors are in `instrument-booklet.md`.
