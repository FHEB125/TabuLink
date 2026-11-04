# TabuLink Applied Changes

This build applies the requested Coordinator/Administrator ownership and usability changes.

## Operational ownership

- Administrators configure programs, events, teams, roles, and system-wide settings.
- Coordinators operate within their assigned scope.
- Coordinators can manage event participants, brackets, and game scheduling within their scope.
- Coordinator-saved data is stored in the shared database and is immediately visible to the Administrator.
- No duplicate Coordinator-only participant/team/schedule datasets are created.

## Score verification

- Score submitters can only create `SUBMITTED` scores.
- Coordinators move scores to `COORDINATOR_VERIFIED`.
- Administrators can make only Coordinator-verified scores officially verified/countable.
- Direct status manipulation through the score form is no longer accepted.

## Correction verification

- Correction requests begin as `PENDING` / awaiting Coordinator approval.
- Coordinator approval moves the request to `COORDINATOR_APPROVED`.
- Administrator approval applies the correction officially.
- Correction target selection is no longer editable through the correction form.

## Navigation and dashboard

- Administrator home is now a program-first hub with clear program buttons/cards.
- Selecting a program opens its program dashboard.
- Console navigation labels were rewritten for clearer everyday language.
- Profile/account controls remain anchored in the upper-right header.

## Login page

- Login screen uses an approximately 50/50 split layout.
- The TabuLink logo is larger.
- The right login half has a dedicated visual holder/corner treatment.
- Responsive behavior remains for tablet/mobile layouts.

## Activity Log

- Activity Log replaces the ambiguous Audit Logs navigation label.
- Filter by exact action, user, and search text.
- Actions include login/logout and all existing recorded system actions such as participant changes, score submissions, verification, correction requests, approvals, deletions, bracket work, schedules, exports, and configuration changes.
- Filtered activity can be exported as CSV.

## Security/workflow hardening

- State-changing operations use POST/CSRF protection where applicable.
- Logout is POST-only.
- Destructive and workflow-changing actions are no longer intended to execute through GET links.
- Bracket/game-result verification remains a Coordinator → Administrator chain.

## Validation performed

- Python compilation: passed.
- Django template compilation: 75 templates, 0 template errors.
- JavaScript syntax checks: passed.
- Django system checks: passed with the archive's broken Pillow binary check (`fields.E210`) explicitly silenced in the audit environment.
- Migration graph: clean; no pending model migrations after applying the new migrations.
- Targeted score workflow tests: passed.
- Targeted bracket/sports/verification regression tests: passed.
- Full 178-test suite was not allowed to finish within the available execution window; no failure was observed in the portion reached after the workflow tests were updated.


## Program Levels and Game Schedule Navigation
- Added the supplied Elementary Level event catalog under Sports, Socio-Cultural Arts, and Ambassadorship.
- Program dashboards now have a level selector and show only events for the selected level.
- Category event saves are level-scoped so events from different levels cannot be mixed or detached accidentally.
- Added a program-level event configuration link that preserves the selected level.
- Added All Programs Administrator Game Schedule filters for program, level, event, and category.
- Added Program Dashboard Game Schedule filters for level, category, event, and game status.
- Preserved the cleaned sample database: administrator retained; sample programs/events/games/scores removed.


## Ambassadorship judging-criteria ordering
- Ambassadorship Coordinator judging workspace now uses dedicated ↑ / ↓ controls for criterion order.
- Manual `display_order` entry is hidden only for Ambassadorship Coordinator criterion add/edit screens; new criteria receive the next order automatically.
- Reordering is restricted to the same Ambassadorship judging stage and automatically normalizes active criteria to consecutive positions.
- Administrator/general criteria configuration is unchanged.

## Ambassadorship Participant Slots + Paired Judge Workspace (2026-09-28)
- Added fixed Ambassadorship participant/pair slots (01..NN) to each matched MR/MS event; setting the count mirrors it to the partner event and locks the sequence once set.
- Added Ambassadorship Coordinator Add Participant form with Candidate Number, Participant Type (MR/MS), Participant Name, and Team/School.
- Candidate number is stored on the participant and is used to pair MR #NN with MS #NN.
- Added a dedicated Ambassadorship participant setup page for the coordinator with the fixed 01..NN pair table.
- Added the participant-management permission to the Ambassadorship Coordinator role.
- Updated the paired MR/MS Judge Workspace to display candidate numbers and retain separate MR/MS sheets side-by-side.
- Added regression tests for fixed candidate slots and score submission to both separate paired sheets.


## High-School Event Catalog Update
- Added the event list supplied in the latest source images to the **High-School Level** master catalog.
- Events are organized under Sports, Socio-Cultural Arts, and Ambassadorship.
- Academic-Literary remains empty because no events for that category were supplied.
- The entries are level-scoped: they appear only when **High-School Level** is selected in Administrator Event Configuration and are not added to College or Elementary catalogs.

## Final end-to-end verification/results fixes
- Added strict event completion gates for judging, special/academic-literary, single elimination, double elimination, round robin, and group-stage schedules.
- Sports/tournament equivalent points are withheld until the tournament is actually complete; the championship/grand-final result controls final placement.
- Judging completion now requires every configured judge to have a complete criterion submission for every active event participant and the corresponding aggregate score to be officially verified.
- Special-event completion now requires finalized results and, when an event roster is configured, results covering the configured participants.
- Added explicit GROUP_STAGE generation using the complete round-robin schedule instead of silently falling back to single elimination.
- Fixed the detailed overall program scoreboard to include Sports, Socio-Cultural Arts, Ambassadorship, and Academic-Literary points plus Total.
- Applied the four-category scoreboard to console and public overall-result tables.
- Added POST-only `Verify All` bulk action in the verification area. Coordinators verify their scoped pending scores/game/special results; Administrators make Coordinator-verified scores/games official and finalize verified special results.
- Made game verification + bracket advancement transactional so a failed advancement rolls back the official verification.
- Converted remaining verification mutations in active templates from GET links to CSRF-protected POST forms.
- Updated event/program completion statistics to use the same strict completion rules.


## Ambassadorship Coordinator Candidate Number Layout
- Changed the Ambassadorship Coordinator candidate roster to a table layout.
- The `No.` column now displays the actual assigned candidate number.
- Removed the separate candidate-number display from the table to avoid duplication.
- Added an Edit button with an inline edit form for candidate number, name, gender, and photo.
- Candidate names no longer display a leading `#`; add/edit validation strips a leading `#` from names.
- Existing backend candidate-number validation and MR/MS pairing logic are preserved.

## Hard-coded Zumba Judging Criteria (College, High-School, Elementary)
- The official two-part Zumba rubric is hard-coded in `events.catalog.EVENT_JUDGING_CRITERIA` and is level-agnostic, so the same sheet follows the event at **College**, **High-School**, and **Elementary**.
- First Part — Group Zumba Performance (70%): Performance, Energy & Execution (40), Choreography (40), Costume & Group Identity (20) — totals 100.
- Final Stage — Flash Mob / Showdown (30%): Energy & Enthusiasm (40), Synchronization & Execution (40), Creativity & Group Identity (20) — totals 100.
- Criteria are auto-seeded whenever a Zumba Judging event is configured from the master catalog, and are also seeded through the event form when *Apply default judging criteria* is checked.
- Reconfiguring a level never duplicates the rubric, and events without a hard-coded preset keep their criteria empty until the Administrator adds them.
- Tabulation blends the two stages with the fixed 70/30 weights (`tabulation.services.STAGED_STAGE_WEIGHTS`), normalising each stage to a percentage before ranking.
- Added regression tests covering rubric seeding at all three levels, non-duplication, the form path, and the 70/30 staged scoring.

## Hard-coded Dance Judging Criteria (Contemporary Dance, Dance Duo, Folk Dance)
- Added the official single-stage rubrics to `events.catalog.EVENT_JUDGING_CRITERIA`, seeded automatically whenever the event is configured from the master catalog (or via the event form with *Apply default judging criteria*).
- **Contemporary Dance** — every level (College + High-School + Elementary). Performance (40), Choreography (40), Relevance of Message, Appropriateness of Music, Costumes & Props (20) — totals 100.
- **Dance Duo** — every level (College + High-School + Elementary). Same 40/40/20 rubric.
- **Folk Dance** — every level (College + High-School + Elementary). Execution & Mastery (40), Choreography & Creativity (25), Costume & Presentation (20), Expression & Stage Presence (15) — totals 100.
- **Folk Dance converted from Non-Judging to Judging** at every level so the rubric applies; the Socio-Cultural Arts form note was updated accordingly.
- **All six presets (Zumba, Folk Dance, Vocal Solo, Vocal Duet, Dance Duo, Contemporary Dance) are catalogued under Socio-Cultural Arts at every level**, so the master list is available to any program — including a program that has not been created yet (the catalog is program-independent and the category row is created lazily on configure).
- Added regression tests covering the three rubrics at each level, non-duplication, and preset availability across all levels.

## Hard-coded Battle of the Bands Rubric (College)
- Added the official single-stage rubric to `events.catalog.EVENT_JUDGING_CRITERIA['Battle of the Bands']` (a College Socio-Cultural Arts event): Planning and Preparedness (10), Musicality (35), Quality of Performance (35), Interface with the audience and Showmanship (20) — totals 100.
- It seeds automatically whenever Battle of the Bands is configured from the College catalog (or created via *Create Event Not in List* / the event form), and the `apply_preset_criteria --name "Battle of the Bands"` command can (re)apply it to an existing event, overwriting its criteria.
- Created the **Battle of the Bands** (College, Socio-Cultural Arts, Judging) event with its rubric in every program, and it stays globally available from the master catalog so any current or future program can add it.
- Added `events.tests.BattleOfTheBandsRubricTests`.

## Hard-coded Little Mr & Ms Intramurals Rubric (Elementary)
- Added the official single-stage rubric to `events.catalog.EVENT_JUDGING_CRITERIA['Little Mr & Ms Intramurals']` (an Elementary Ambassadorship event): Production Number (20), School Uniform (20), Sportswear (20), National Hero Attire (20), Question & Answer (20) — totals 100.
- Added `('Little Mr & Ms Intramurals', 'JUDGING', '')` to `ELEMENTARY_AMBASSADORSHIP`, so it is globally available from the master catalog at the Elementary level for any current or future program.
- `configure_catalog_events` now configures any Ambassadorship event whose name contains "Mr & Ms" as a paired pageant (`ambassadorship_candidate_scope='MR_MS'`, `ambassadorship_pair_judging_enabled=True`).
- Created the **Little Mr & Ms Intramurals** (Elementary, Ambassadorship, Judging, paired) event with its rubric in every program.
- Added `events.tests.LittleMrMsIntramuralsRubricTests`.

## Backfill presets into previously-created events (`events.0032`)
- Added data migration `events.0032_backfill_preset_judging_criteria`: every existing non-Non-Judging event whose name matches a preset (Vocal Solo, Vocal Duet, Zumba, Contemporary Dance, Dance Duo, Folk Dance) and has **no criteria** is seeded with the official rubric, so events created before a preset existed get it too.
- Events that already carry criteria (hand-entered or custom) are left untouched, matching the runtime seeding rule. The migration is reversible (reverse removes exactly the preset rows it could have created) and covered by `events.tests_preset_backfill_migration`.

## Apply/overwrite a preset rubric on a specific event (`apply_preset_criteria`)
- The preset is now authoritative for an event named after it: `_seed_event_criteria` and the event form's *Apply default judging criteria* checkbox **replace** the event's existing criteria with the full official rubric instead of skipping when criteria already exist (the event form help text says so).
- Added management command `python manage.py apply_preset_criteria` to (re)apply a preset to existing events by name, overwriting their criteria: `--name "Folk Dance"` (repeatable) targets one or more event names, `--dry-run` reports without writing, and no `--name` applies every preset.
- Added `events.tests.PresetRubricOverwriteTests` covering the command (real + dry-run), the seeding helper, and the event-form edit path.

## Global catalog: previously program-specific events promoted (College)
- Added the events that existed only inside one program to the global `MASTER_CATALOG` College lists so any current or future program can configure them:
  - Sports: `Football` (Non-Judging).
  - Socio-Cultural Arts: `Academic`, `Band Marching` (Judging).
  - Ambassadorship: `Ambassadorship`, `Mr & Ms SJCB`, `Mr & Ms Josephian` (Judging). The two `Mr & Ms` pageants are auto-configured as paired (`MR_MS`).
- Updated `events.tests.CollegeEventConfigCatalogTests` and the configuration-count assertions (College Sports 18→19 entries / 35→36 expanded; Socio-Cultural 14→16; Ambassadorship 2→5; total 57).

## Judge edit-permission (correction) flow on every judged event
- `console.views._supports_judging_corrections` now returns True for **every** event whose `requires_judging` is set (Judging and Special Case), not only Ambassadorship and `Vocal Solo`/`Vocal Duet`. A judge can now request permission to edit a submitted score on any judging event (Zumba, Folk Dance, Contemporary Dance, Dance Duo, Battle of the Bands, Chorale, etc.).
- Approval stays with the existing coordinator roles (`ambassadorship-coordinator`, `socio-cultural-coordinator`). Removed the now-unused `VOCAL_JUDGING_EVENT_NAMES` / `_is_vocal_judging_event`.
- Added `console.tests.JudgingCorrectionSupportTests`.

## High-School Mr & Ms Intramurals — SDG Advocacy two-track judging
- The official **Mr & Ms Intramurals** (High-School, Ambassadorship) rubric now spans three stages in `events.catalog.EVENT_JUDGING_CRITERIA`:
  - **First Part (75)** — Production Number (15), School Uniform (20), Abbaggaoan Cultural Attire (20), Sportswear (20).
  - **SDG Advocacy (25)** — SDG Knowledge and Understanding (5), Relevance and Significance (5), Clarity and Effectiveness of Message (5), Creativity and Video Presentation (5), Impact and Call to Action (5).
  - **Final / Q&A (100)** — Relevance (25), Clarity (25), Depth of Knowledge (25), Confidence and Delivery (25).
- Added the `ADVOCACY` value to `Criterion.STAGE_CHOICES` and the `SDG_ADVOCACY_JUDGE` value to `EventCoordinator.ROLE_CHOICES` (migration `events.0033_criterion_sdg_advocacy_and_judge_role`).
- **RBAC:** the dedicated SDG Advocacy judge is an `EventCoordinator(role='SDG_ADVOCACY_JUDGE')` account (application role `judge`). `users.OPERATIONAL_EVENT_ROLES['judge']` now covers both `JUDGE` and `SDG_ADVOCACY_JUDGE`, so `can_access_event` / `accessible_event_ids` admit either assignment to the event.
- **Two independent judging tracks, no Top-5 cut:** `console._render_sdg_advocacy_judging` gives regular pageant judges the First Part + Final (Q&A) criteria and the SDG Advocacy judge only the Advocacy criteria (via `SdgAdvocacyScoreForm`). Every candidate advances to the Q&A Final, so the Top-5 / 50-50 ambassadorship flow is bypassed for SDG events.
- **Tabulation:** `tabulation.services.STAGED_STAGE_WEIGHTS['Mr & Ms Intramurals']` uses the grouped form `((('FIRST_PART', 'ADVOCACY'), 60), (('FINAL',), 40))`; `_normalized_stage_groups` / `_staged_point_average` pool the Preliminary (First Part 75 + Advocacy 25) and blend it 60/40 with the Q&A Final. `_judging_event_is_complete` recognises the two-track format.
- The coordinator release panel (`_ambassadorship_control_entry` / `_ambassadorship_release.html`) shows the official Preliminary 60% + Q&A 40% standings instead of the Top-5 and 50/50 panels for SDG events; the coordinator event page (`console:coordinator_event`) renders it without the Top-5 panels; the per-candidate 50/50 breakdown link is suppressed.
- Added tests: `tabulation.test_configured_formulas.HighSchoolMrMsStagedTests` (grouped weights, 60/40 blend, incomplete-Advocacy exclusion) and `console.tests_sdg_advocacy.SdgAdvocacyJudgingTests` (per-track visibility, submission, disabled and unassigned access).

## Unified College Mr. & Ms. Intramurals — paired pageants with the defaults rubric
- The separate College `Mr. Intramurals` and `Ms. Intramurals` events now drive one unified **Mr. & Ms. Intramurals — College Year Level** workflow: `events.catalog.configure_catalog_events` auto-enables `ambassadorship_pair_judging_enabled` on both, so a single judge sheet scores the MR and MS columns side-by-side (the same paired flow as the `Mr & Ms` pageants) while each event keeps its own `FIRST_PART`/`FINAL` staged standings. The event form (`console.forms.EventForm.save`) applies the same pairing.
- `events.defaults` is now the single source of truth for the rubric. New `events.catalog.unified_mr_ms_college_criteria()` maps `defaults.PRELIMINARY_CRITERIA` (5 criteria) to the `FIRST_PART` stage and `defaults.FIRST_QA_CRITERIA` (4 criteria) to the `FINAL` stage, carrying each criterion's `max_score`/`min_score`. `_seed_event_criteria` and the event form's *Apply default judging criteria* checkbox seed this 9-criterion rubric (each stage totalling 100); the *Final Q&A* pairing is intentionally left out for now.
- Fixed the corrupted `events.defaults.UNIFIED_MR_MS_COLLEGE_NAME` (`U+FFFD` → a plain hyphen).
- `tabulation.services.STAGED_STAGE_WEIGHTS['Mr. Intramurals']` / `['Ms. Intramurals']` blend `FIRST_PART` 50% + `FINAL` 50%, so the official standings match the coordinator's 50/50 final while the Top-5 progressive release flow is unchanged.
- Added tests: `events.tests.UnifiedMrMsCollegeCriteriaTests` (catalog presence, pair flag, defaults rubric seeding via catalog and form, 50/50 weights, no duplication, clean defaults name) and `tabulation.test_configured_formulas.CollegeMrMsStagedTests` (50/50 declaration and blend, incomplete-Final exclusion).

## Unified College Mr. & Ms. Intramurals — Top-5 qualification + distinct Final Q&A round
- **Qualification is now the official 50/50 blend** of the Preliminary (`FIRST_PART`, 5 criteria) and the first Question & Answer (`FINAL`, 4 criteria) per division. `_ambassadorship_top5` used to rank on `FIRST_PART` alone, so the Top-5 (and therefore who reached the final) did not match the coordinator's 50/50 final.
- **A distinct Final Q&A round now exists** to decide Mr./Ms. `FINAL_QA_CRITERIA` was dead code; a new `FINAL_QA` value was added to `Criterion.STAGE_CHOICES` (migration `events.0034_criterion_final_qa_stage`, **not applied**). `events.defaults.FINAL_QA_CRITERIA` stores Beauty & Handsomeness 40 and Intelligence / Substance of Answer 60 as the criterion *maximum* (weight-as-max, like the Zumba 40/40/20 rubric), so the stage total is the candidate's weighted 100-point Final Q&A result.
- `events.catalog.unified_mr_ms_college_criteria()` now seeds **11** criteria: 5 `FIRST_PART` + 4 `FINAL` + 2 `FINAL_QA`. Detection is rubric-based, not name-based: `_is_unified_mr_ms_college_pageant(event, criteria)` is true only when an active `FINAL_QA` criterion exists, so unrelated Ambassadorship events (and the High-School SDG format) keep their existing behaviour.
- **Scoring helpers (`console.views`):** `_ambassadorship_qualification_complete` requires both `FIRST_PART` and `FINAL` for unified events; `_ambassadorship_top5` blends them 50/50 per side (skipping incomplete candidates, never treating a missing stage as 0); `_ambassadorship_final_qa_result` averages each judge and normalises against the 40/60 maximum, returning `None` until every judge has scored every Final Q&A criterion; `_ambassadorship_final_result` returns the Final Q&A result as the winner (`final_score`), and `_ambassadorship_finalists` ranks finalists per category on it. A Final Q&A score can never leak into the Top-5 ranking.
- **Final Q&A is finalist-only.** In the paired judge branch a separate `FINAL_QA` form is rendered (`sheet_round=FINAL_QA`, hidden field), scoped to the per-side Top-5 via `_ambassadorship_paired_bands(..., 'final_qa_criteria', 'final_qa_roster', 'final_form')`; the POST dispatch writes only the finalists' rows. The single-event branch gates `FINAL_QA` criteria the same way (`final_available`, eligible participants limited to the Top-5).
- **Tabulation:** `tabulation.services.STAGED_STAGE_WEIGHTS['Mr. Intramurals']` / `['Ms. Intramurals']` is now `{'FINAL_QA': Decimal('100')}`, so the official standing is the Final Q&A round (normalised to a percentage) instead of the 50/50 qualification. `judging_standings` now also honours `Criterion.minimum_points` (an out-of-range score is excluded, mirroring the judging-sheet `min_value`/`max_value`; the default floor is 0, leaving events that never set one unchanged).
- **Templates:** `templates/console/judge/event.html` gains the Final Q&A section (Finalists only, 40/60 note); `coordinator/_ambassadorship_release.html` shows the "Prelim 50% + First Q&A 50% → Top 5 → Final Q&A" pill, the Qualification 50/50 Top-5 column and the Final Q&A results columns; `coordinator/ambassadorship_candidate_breakdown.html` labels the Qualification / Final Q&A metrics and the formula line for the College pageant.
- **Tests:** new `console/tests_college_mr_ms_scoring.py` (15 tests: detection, two-stage qualification gate, combined 50/50 ranking, Final Q&A excluded from qualification, 40/60 weighting, winner differing from the qualification leader, incomplete Final Q&A, finalist-only sheet rendering, finalist-only POST persistence, qualifying POST never writing Final Q&A). Updated `events.tests.UnifiedMrMsCollegeCriteriaTests` (11-criterion rubric, Final Q&A weights) and `tabulation.test_configured_formulas.CollegeMrMsStagedTests` (Final Q&A declaration/blend, missing Final Q&A exclusion).
- **Migration (run later, once):** `python manage.py migrate events 0034_criterion_final_qa_stage`. Existing events seeded before this change carry only the 9-criterion rubric; re-seeding is required for them to gain the `FINAL_QA` criteria and the new behaviour.




