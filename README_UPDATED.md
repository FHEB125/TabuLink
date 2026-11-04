# TabuLink — Updated Implementation

This package contains the updated SJCB Event Tabulation and Dissemination and Management System implementation aligned with the current institutional FRD and business rules.

## Major changes applied

- Administrator-controlled user account management with primary + additional roles.
- Institutional / Departmental / Event account scope fields.
- Team Department/Section represented and Team Logo fields.
- Program search and status filtering.
- Competition ranking (`1, 1, 3, 4`) instead of dense ranking (`1, 1, 2, 3`).
- Special points can be marked as excluded from overall standing (for example, Most Disciplined or Cleanest Area).
- Event-instance participating teams, coordinator/OIC, venue, bracket lock state and bracket-generation metadata.
- Automatic Single Elimination and Round Robin bracket generation with draw randomization.
- Bracket locking and automatic schedule generation.
- Two-stage score verification fields for coordinator verification and administrator confirmation.
- Two-stage correction approval fields for coordinator and administrator actions.
- Judging tabulation based on criterion-level submissions for Point Average and Ordinal Rank-Sum.
- Running/final program-state calculation.
- Program result Print view.
- PDF, Excel/XLSX and CSV result export.
- Administrator-only complete result/data backup as ZIP.
- Backup list and protected backup download endpoints.
- Backup contains structured JSON data and media files while excluding user passwords.
- Environment-based database and secret-key configuration with SQLite fallback for development.

## Important setup

The project now defaults to SQLite for a clean local development setup. PostgreSQL can be enabled with:

- `DB_ENGINE=postgresql`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`

Set `DJANGO_SECRET_KEY` in a real deployment. Do not commit production secrets.

Install dependencies:

```text
pip install -r requirements.txt
```

Then:

```text
python manage.py migrate
python manage.py test
python manage.py runserver
```

## Administrator result export

Open a program's Results page and use:

- Print
- PDF
- Excel
- CSV

The export uses the same tabulation service used by the console, so exports do not recalculate results independently.

## Administrator backup

Open **Console → Exports & Backups → System Backups**.

A full backup contains structured system records and media. Program-specific backups are also available from the program detail page.

Backup files are stored under the configured `TABULINK_BACKUP_ROOT` (default: `backups/`). The download endpoint is authenticated and permission-protected.

## Architecture note

The active Django applications are the root-level `users`, `programs`, `events`, `scores`, `tabulation`, and `console` applications listed in `tabulink/settings.py`. The original ZIP contained an older duplicate copy under `tabulink/`; that inactive copy is not part of the active runtime architecture.

## Validation performed

- Python syntax compilation across the active source tree: passed.
- Django template compilation: passed for all templates.
- Clean migration run on a temporary SQLite database: passed.
- Existing project test suite: **16 tests passed**.

The local validation environment could not load the bundled Windows Pillow binary under Linux, so Django's `fields.E210` ImageField system check was silenced only during the local test run. The project already required Pillow before these changes; install the requirements on the target machine to run the normal unsilenced check.

## FRD-Aligned Access and Score Submission Workflow

- **Administrator**: manages users, programs, teams, categories, events, event configuration, special points, verification/final confirmation, corrections, tabulation/publication, exports, and backups. The administrator is **not an operational score/result submitter**.
- **Event Manager**: submits non-judging game/event results and requests corrections for assigned events/instances only.
- **Judge**: submits judging scores per contestant and criterion for assigned judging events only.
- **Coordinator**: reviews/coordinates verification and correction workflows and can generate/lock assigned brackets/schedules; does not submit operational scores.
- **Verification**: submitted operational results remain pending until coordinator verification; administrator confirmation is required before final verification for the Score/GameResult verification chain.
- **Event scoping**: non-administrator accounts can only open event data for events explicitly assigned to them (EventCoordinator assignment, EventInstance assignment where applicable, or their explicit event scope). Direct URL access is checked server-side.
- **Dashboards**: login routing sends each operational account to its role dashboard; dashboard navigation is role-aware.

## Config-driven tabulation formulas

The tabulation engine does not contain event-specific point values. Numeric
values used for event scoring must come from the Administrator's event
configuration or from verified submitted results.

### Judging: Point-Average per Criterion

For each active criterion:

`Criterion Average = Sum of judge scores for the criterion / Number of submitted judge scores`

Then:

`Final Judging Score = Sum of all calculated Criterion Averages`

The maximum for each criterion is the Administrator-configured `Criterion.points`.
A judge cannot submit a value outside that configured maximum.

### Judging: Ordinal Rank-Sum per Criterion

For each active criterion, contestants are ordered by their criterion average
and assigned ordinal ranks. The contestant's final metric is:

`Final Rank Sum = Sum of ordinal ranks across all active criteria`

Lower rank sum is ranked higher. The system uses competition ranking for ties.

### Non-Judging: Win/Loss

For every verified game, the engine adds the Administrator-configured value
for the applicable outcome:

- Win → configured Win Points
- Loss → configured Loss Points
- Disqualification → configured DQ Points
- Forfeit → configured Forfeit Points
- No Entry → configured No-Entry Points

The event ranking is based on each team's accumulated configured result points.
No fallback point value is generated by the system.

In Placement / Distance scoring the same outcome values apply consistently:
DQ uses the lowest configured placement-equivalent points, while Forfeit and
No Entry use their configured outcome values, whatever place the team's
measured results would otherwise produce.

### Placement / Distance

The Administrator selects the result type and, for measured results, whether
higher or lower is better. The system ranks the verified results and converts
the final rank using the Administrator's placement-equivalent list.

For example, if the Administrator enters a placement list, the first value is
used for 1st place, the second for 2nd place, and so on. Every place below the
last number in the list is paid that last number, so a list of `50, 30, 20, 10`
gives 10 points to 5th place and anything below it. A special outcome is scored
from its own configuration rather than the placement rank: DQ gets the lowest
configured placement-equivalent, and Forfeit / No Entry get their configured
outcome points. Zero points is reserved only for a scope with no configured
value at all. The software does not assume any particular values.

### Category and Overall Standing

Each event contributes its calculated `points` value to the category. Category
contributions are then summed into the overall program standing, together with
Special Points whose `counts_toward_overall` flag is enabled. Competition
ranking is used for ties: `1, 1, 3, 4, ...`.


## Ambassadorship criterion minimum score

Ambassadorship Event Managers can now configure both Lowest Score and Maximum Score for each judging criterion. Judge score fields enforce the configured range, and a criterion cannot be saved with a lowest score higher than its maximum. Existing criteria default to a lowest score of 0.00.
