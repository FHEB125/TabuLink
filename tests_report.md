# Tests — Ambassadorship results on Administrator and Public pages

## Objective
`console:results` (Administrator) and the public pages (`public_results`,
`public_event_results`, program detail event list) now show Ambassadorship
results with the **same per-category structure and organisation as the
Coordinator view**: separate Ms. / Mr. sections, identical candidate ordering,
criterion scores, and per-category final results.

The shared builder `console.views._ambassadorship_display_boards(event,
verified_only=False)` is the single source for all three surfaces. Public
surfaces pass `verified_only=True` so pending/unverified judge scores can never
leak onto a published page.

## Files changed
- `console/views.py` — `_ambassadorship_display_boards` (shared builder);
  `_verified_judging_keys`; `verified_only` threaded through
  `_judge_has_submitted_criterion`, `_ambassadorship_qualification_complete`,
  `_ambassadorship_candidate_score_breakdowns`,
  `_ambassadorship_candidate_stage_result`, `_ambassadorship_top5`,
  `_ambassadorship_final_qa_result`, `_ambassadorship_final_result`,
  `_ambassadorship_finalists`, `_ambassadorship_control_entry`;
  `coordinator_event` refactored onto the shared builder;
  `results()` `selected_event` gains `ambassadorship`.
- `console/views_helper.py` — `build_public_cards` lazily builds a
  verified-only `ambassadorship` board per event (`has_scores` flag).
- `tabulink/public_views.py` — `public_program_detail` and
  `public_event_results` attach the verified-only `ambassadorship` board.
- `templates/console/results/results.html` — criterion-scores + final-results
  sections per category (`amb-result-side`), after the existing standings.
- `templates/tabulation/_public_ambassadorship.html` (new) — public per-category
  sections, rendered only when `has_scores`.
- `templates/tabulation/public_results.html`, `public_event_results.html`,
  `_public_event_results_list.html` — branch on the `ambassadorship` board.
- `static/css/console.css` — `.amb-result-side` alias.
- `static/css/public.css` — `.pub-amb-*` / `.pub-muted` styles.
- New test module: `console/tests_ambassadorship_results_display.py` (9 tests).

## Safety constraints kept
No migration changes (`makemigrations --check` still reports only the two
pre-existing model-drift migrations). Scoring/ranking formulas, judging
criteria, stage weights, and equivalent-point rules untouched. Coordinator page
unchanged. No candidate names/rankings hard-coded in production code — scores
and ranks come from the same judging data as the Coordinator view.

## Test runs

| Run | Scope | Result |
|-----|-------|--------|
| `manage.py check` | system | `0 silenced.` |
| targeted regression (ambassadorship display, per-category ranking, single-event split, paired MR/MS, special-awards public, college MR/MS scoring, judging individual scope) | 61 tests | OK |
| `console.tests_ambassadorship_results_display` (new) | 9 tests | OK |
| full suite `manage.py test` | **569 tests (661s)** | **OK** |

## New-test coverage (`console/tests_ambassadorship_results_display.py`)
- Admin page renders exactly two `amb-result-side` panels (Ms. then Mr.),
  each holding only its own category's candidates, numbered, with criterion
  scores and totals; no duplicate panels/numbers; no raw `{%`/`{{` leakage.
- Admin final-results order matches the per-category ranking.
- Public home cards and event page show per-category sections only when
  published; combined "Winner:" tag suppressed.
- Surfaces agree on ordering, ranks and final scores (full and verified boards).
- A third, unverified judge's scores appear on the Administrator page but never
  on a public page (verified-only filtering).
- Private program exposes nothing publicly (404 on the event page).
- Unverified event renders a graceful empty state.
- Non-Ambassadorship judging event keeps its plain combined standings table.