# Deploying TabuLink to Render

TabuLink is a Django app (Django 5.2, Python 3.11). This guide is written to match the project's current configuration (WhiteNoise for static files, `STORAGES` dict, PostgreSQL optional).

## 1. Prepare the repo
1. Push the repository to GitHub/GitLab.
2. In Render, create a **Web Service** from that repo (Python).
3. Build command: this is a **Render dashboard setting** and is not stored in this repository, so it cannot be verified from the code. The repository ships `build.sh`:

   ```bash
   #!/usr/bin/env bash
   set -o errexit

   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt

   python manage.py migrate --noinput
   python manage.py collectstatic --noinput
   ```

   If the Render Build Command is set to `./build.sh` (or `bash build.sh`), the build **also runs migrations automatically** on every deploy — see §3A. If the dashboard instead uses a command without `migrate` (as earlier versions of this guide showed), migrations do **not** run during the build and must be applied deliberately. **Which command the dashboard uses is unverified; check Render → Service → Settings before relying on either behaviour.**
4. Start command: `Procfile` defines `web: gunicorn tabulink.wsgi:application --bind 0.0.0.0:$PORT`. In the dashboard, use `gunicorn tabulink.wsgi:application` (Render supplies `$PORT`).

## 2. Required environment variables
Render Dashboard → Service → Environment → Add Environment Variable. **Set names only as shown; never paste secret values into logs or issues.**

| Variable | Value | Notes |
| --- | --- | --- |
| `PYTHON_VERSION` | `3.11.9` | Match local/CI. |
| `DJANGO_ENV` | `production` | Enables production security headers and requires `DJANGO_SECRET_KEY`. |
| `DJANGO_SECRET_KEY` | *(generate)* | Long random string. |
| `DJANGO_DEBUG` | `0` | Must be off in production. |
| `DJANGO_ALLOWED_HOSTS` | `your-app.onrender.com` | Comma-separated if multiple. |
| `DJANGO_SECURE_SSL_REDIRECT` | `true` | Usually `true` behind Render. |
| `DATABASE_URL` | *(Render Postgres internal URL)* | If using Render Postgres. Or use `DB_ENGINE=postgresql` + `DB_*` vars. See §3. |
| `WEB_CONCURRENCY` | `2` | Optional tuning. |

## 3. Database (Postgres)
If you add **Render Postgres**, Render injects `DATABASE_URL`. Django's settings can read `DATABASE_URL` only if you wire `dj-database-url` (not present by default). Easiest: use the discrete vars with `DB_ENGINE=postgresql`:

```
DB_ENGINE=postgresql
DB_NAME=...
DB_USER=...
DB_PASSWORD=...
DB_HOST=...
DB_PORT=5432
```

Migrations are **not** scoped to a feature or app: `python manage.py migrate` applies **every pending migration in every installed app**. Read §3A before running it against production. Do not run it from a checkout that points at production unless you intend to apply everything that is pending.

Create an admin/superuser as needed.

## 3A. Migrations on Render (read before deploying)

### What the repository actually does
- `build.sh` runs `python manage.py migrate --noinput` (line 7), then `collectstatic`. It exits on the first error (`set -o errexit`).
- `Procfile` contains only the `web` process. It has **no** `release:` entry, so nothing in the repository runs migrations at process start.
- There is no `render.yaml` (or equivalent) in the repository. Build, start, and pre-deploy commands live in the **Render dashboard** and are **unverified from the code**.

### Automatic migration behaviour
- If — and only if — the Render Build Command executes `build.sh`, every deployment applies **all pending migrations for all apps**, not just the ones related to the feature being deployed.
- Because the build runs before the new instance is started, migrations are applied **while the previous version is still serving traffic**. New code is only activated after a successful build/start.
- If a migration fails, `set -o errexit` fails the build. Render then keeps the previous deploy live (platform behaviour; confirm in the Render docs for the service). Migrations already committed in the same run stay applied; the failed migration's own transaction is rolled back on PostgreSQL (Django runs migrations atomically by default). The deployment is left in a **partially migrated** state that must be inspected before retrying.
- `manage.py migrate` runs Django system checks first. In production, an unsafe evidence-storage configuration raises `scores.E001` and **blocks migrations (and therefore the build)** before anything is applied. Do not work around this with `--skip-checks`; fix the configuration instead.
- A dashboard **pre-deploy command** or one-off job (if the plan exposes one) can also run migrations. That is a dashboard setting, not repository evidence.

### Why automatic "migrate everything" is risky
- **Unrelated pending migrations** are applied by accident. A branch can contain migrations from unrelated work; deploying it applies them all.
- **Destructive / irreversible migrations.** TabuLink has real examples:
  - `events.0010` and `events.0013` remove model fields; `scores.0019` and `scores.0027` remove fields. Dropped columns and their data cannot be restored by reversing the migration.
  - `users.0029_remove_committee_in_charge_role` deletes the CIC role and its assignments, and its reverse is a no-op.
  - `events.0038_remove_committee_in_charge_event_assignments` deletes rows, and its reverse is a no-op.
  - `users.0022` (team scope → level), `users.0023` (notification backfill), `scores.0021` (derive winners), `scores.0023`, and `scores.0025` use `RunPython.noop` reverses, so they are effectively one-way.
- **Data migrations that rewrite rows.** `events.0027`, `events.0032`, `events.0036`, `scores.0023`, `scores.0025`, `users.0019`, `users.0023`, and `programs.0014` iterate over table data. They are small on today's data set but can be slow or lock rows as data grows.
- **Code/migration coordination.** `users.0028` renames role display names, `users.0029`/`events.0038` remove the CIC role and assignments, and `events.0037` removes `COMMITTEE_IN_CHARGE` from `EventCoordinator.role` choices. Applying these without the matching application code (or deploying code that still writes the retired value) causes inconsistent data or errors.
- **Cross-app ordering.** Dependencies are enforced (`users.0029` depends on `events.0038`; `scores.0031` depends on `events.0036`), but a partial failure can still leave one app ahead of another.

### Inspect pending migrations before deploying
Run these with the **target** database environment variables set (and `sslmode=require` for a remote database). They are read-only:
```bash
python manage.py showmigrations
python manage.py migrate --plan
```
`migrate --plan` prints exactly what `migrate` would apply, in order, without applying it. Review every listed migration and its file before deploying. Do **not** point a local checkout at production just to inspect it unless you understand that `migrate` in the same shell would write.

For a strictly read-only history check (no Django), use the PostgreSQL client:
```sql
SELECT app, name, applied FROM django_migrations ORDER BY app, id;
```

### Verify history after deploying
- `python manage.py showmigrations` should show `[X]` for the expected migrations.
- `python manage.py migrate --check` exits non-zero if anything is still unapplied (it does not apply anything).
- Read-only SQL: `SELECT app, name FROM django_migrations WHERE app IN ('users','events','scores') ORDER BY id;`

### If a migration fails
1. Treat the deploy as failed; do not repeatedly redeploy hoping it passes.
2. Inspect `django_migrations` to see which migrations were applied and which failed.
3. Read the failing migration and its dependencies; fix forward with a new migration or correct the data/configuration.
4. Never hand-edit `django_migrations`, and never fake-apply a migration unless you have verified the schema/data state.
5. If data was destroyed, restore from a backup (see below) before retrying.

### Backups
- Before any **destructive** (field/table/row removal) or **irreversible** (`RunPython.noop` reverse) migration, take a restorable backup. On Render, backup/PITR availability depends on the plan; the Free plan may not include it. Verify the plan's retention before relying on it.
- Do not assume a backup exists. Record where it is and test that it can be restored.
- Creating a backup/dump may incur storage or plan costs — treat it as an action that needs explicit approval.

### Controlled migration without Render Shell access
Render Shell is not available here, so a controlled process is:
1. Review `migrate --plan` and the migration files locally.
2. Rehearse on a production-like database (same PostgreSQL major version) with a copy of the data.
3. Get explicit approval for the exact migration list.
4. Apply via **one** controlled path: a dashboard pre-deploy command / one-off job, or a trusted machine using the production connection string supplied through an environment variable (never pasted into a file, log, or commit).
5. Verify `django_migrations` and the affected tables immediately after.
6. Keep the previous application version deployable until verification passes.

### Actions that require explicit approval
- Running `migrate` against production (in any form).
- Applying, faking, or reversing any migration.
- Creating a backup/dump (possible storage or plan cost).
- Changing the Render Build Command, pre-deploy command, start command, or any environment variable.
- Deploying, or re-deploying to recover from a failed migration.
- Any direct SQL write, or data repair/backfill.
- Reassigning or deleting user accounts/roles.

### Recommended future workflow (not implemented)
This is a recommendation only; `build.sh` and the Render configuration are unchanged.
1. Keep migrations out of the build command; run them as an explicit, approved step.
2. Before each release, run `showmigrations` and `migrate --plan` against a staging copy and review the full list.
3. Classify each pending migration as safe / destructive / irreversible / long-running.
4. Require a tested backup before destructive or irreversible migrations.
5. Deploy code and migrations in a known order (expand → deploy → contract) when they must coordinate.
6. After deploy, verify `django_migrations` and smoke-test the affected flows.

## 4. Persistent uploads (logos/avatars/images)
On Render the web service filesystem is **ephemeral**. Any file written to local disk disappears on restart or redeploy. For images stored via `STORAGES['default']` (program logos, participant/profile images), use an **S3-compatible** bucket.

### Option A: AWS S3
Set:
```
USE_S3_MEDIA=1
AWS_ACCESS_KEY_ID=<your access key>
AWS_SECRET_ACCESS_KEY=<your secret access key>
AWS_STORAGE_BUCKET_NAME=<bucket name>
AWS_S3_REGION_NAME=<region, e.g. us-east-1>
```

### Option B: Cloudflare R2 / Backblaze B2 / DigitalOcean Spaces
Set the same `USE_S3_MEDIA=1` and keys, plus:
```
AWS_S3_ENDPOINT_URL=https://<accountid>.r2.cloudflarestorage.com
AWS_S3_REGION_NAME=auto
```

Optional:
```
AWS_S3_CUSTOM_DOMAIN=<your public bucket domain>   # only if you serve public media through it
```

> **Bucket privacy for public media:** If you use a custom public domain or a bucket policy that serves public objects, ensure you understand what is public. Public media uses unsigned URLs (`AWS_QUERYSTRING_AUTH=False` for `default`). This is separate from **private evidence** below.

Redeploy. New uploads now go to the bucket and survive redeploys.

> Nothing is operational until these variables are set. Until then the app
> falls back to local filesystem storage for `default` media (fine for local
> dev, **not persistent on Render**).

## 5. Copy existing uploaded files into the bucket

Existing uploaded files live under `media/` on the machine that holds them (your local checkout and/or the deployed instance). After the bucket is configured, copy them once so the relative paths already stored in PostgreSQL resolve against the bucket:

```
# Local machine, with the S3 env vars set. TABULINK_SYNC_MEDIA=1 authorizes it.
# Windows (cmd/PowerShell):
set TABULINK_SYNC_MEDIA=1
python manage.py sync_media --dry-run   # preview only, writes nothing
python manage.py sync_media             # upload missing files
set TABULINK_SYNC_MEDIA=
# macOS/Linux: use `export TABULINK_SYNC_MEDIA=1` / `unset TABULINK_SYNC_MEDIA`.
```

The command is read-only on `MEDIA_ROOT`, never deletes anything, skips files that already exist unless `--overwrite` is passed, and refuses to run while the storage backend is still the local filesystem. File names are preserved, so no database record needs to be edited.

## 6. Evidence attached to result edit-permission requests

An Event Manager who asks to edit a **locked** result must attach a supporting photo or document. That file is **not** public media: it is written to a **separate storage alias** (`STORAGES['evidence']`) whose location sits **outside** `MEDIA_ROOT`, and it is only ever handed out by the authenticated console view `console:permission_request_evidence` after the same scope checks the review queue applies. There is **no public URL** for it.

### Persistence and privacy (required in production)
The evidence store follows the same `USE_S3_MEDIA` switch as public media:

| Situation | Where evidence is stored | Persistent? |
| --- | --- | --- |
| `USE_S3_MEDIA=1` | S3-compatible bucket, prefix `private-evidence/` (separate from public media) | **Yes** |
| `USE_S3_MEDIA` unset/false | `PRIVATE_MEDIA_ROOT` on the local disk (default `BASE_DIR/private_media`) | **No** on Render — **ephemeral** |

**Production policy (fail-closed):**
- In **production** (`DJANGO_ENV=production`), TabuLink **requires a persistent, private evidence store**. If `USE_S3_MEDIA` is not enabled and the evidence backend remains local, `manage.py check` will report an error (`scores.E001`) and the application will refuse new evidence uploads at the form and storage level.
- In **development/tests**, the requirement is relaxed by default so you can work locally with temporary filesystem storage.
- The safeguard **does not** silently fall back from S3 to local storage. If S3 is selected, the evidence backend must be configured privately and correctly, or uploads will be refused.

### Required environment variables (names only)
When using S3 for evidence (required in production), set:

```
USE_S3_MEDIA=1
AWS_ACCESS_KEY_ID=<key>
AWS_SECRET_ACCESS_KEY=<secret>
AWS_STORAGE_BUCKET_NAME=<bucket>
AWS_S3_REGION_NAME=<region>        # or auto for R2-compatible endpoints
AWS_S3_ENDPOINT_URL=<endpoint>     # only for R2/B2/Spaces/custom endpoints
```

Optional:
```
TABULINK_REQUIRE_PERSISTENT_EVIDENCE=auto  # auto|1|0  (default: auto)
TABULINK_EVIDENCE_URL_TTL=300             # seconds (default: 300)
TABULINK_PRIVATE_MEDIA_ROOT=<path>        # local only, NOT recommended on Render
TABULINK_EVIDENCE_MAX_BYTES=5242880       # default: 5 MiB
```

### How evidence is secured
- **Private by design:** evidence is outside `MEDIA_ROOT`; served only by `console:permission_request_evidence` with permission/scope checks and self-review blocking.
- **Signed URLs (S3):** when `USE_S3_MEDIA=1`, the evidence backend uses `querystring_auth=True` with `location='private-evidence'`. **Explicit expiration** is configured via `AWS_QUERYSTRING_EXPIRE` / `querystring_expire` (default **300 seconds**). Evidence objects are **never** public, have **no custom domain**, and **no public ACL** is applied.
- **Content validation:** accepted types `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.pdf`. Validated by **real content** (magic bytes, full image decode for images, PDF header and trailer). Stored under a generated, unguessable name in `result_permissions/`.
- **Headers:** the download response sets `X-Content-Type-Options: nosniff` and a restrictive `Content-Security-Policy`.

### Verify bucket privacy and prefix (before enabling the workflow)
1. **Bucket policy:** ensure the bucket is **not** publicly readable. Do **not** add a `s3:GetObject` allow for `*` to the `private-evidence/` prefix.
2. **Prefix check:** evidence keys must live under `private-evidence/result_permissions/...`. The code enforces this - do not override to a public prefix.
3. **Signed URLs only:** with no custom domain and `querystring_auth=True`, requests must present valid, unexpired signed query parameters.
4. **Staging test (safe):** in a non-production staging environment with S3 configured, upload evidence to a request, download via the review queue/evidence view, confirm it works, redeploy/restart, and confirm the file is **still accessible** (proves persistence). Do **not** test by guessing a public URL.
5. **Fail-closed check:** in staging with `DJANGO_ENV=production` and `USE_S3_MEDIA` unset, run `python manage.py check` - it should report `scores.E001`. New uploads should be refused until S3 is configured.

### If persistence is missing
If evidence files disappear after deploy/restart, **treat this as a deployment blocker**. Reconfigure S3 with the variables above, redeploy, and re-upload evidence if needed (existing DB rows remain but their files would be gone on ephemeral storage).

## 7. Verify

1. `python manage.py check` -> no issues (in production, will fail if evidence storage is unsafe).
2. Open a program/team/participant/profile page and confirm images load from the bucket domain (`https://...`) if using a public bucket/domain for `default` media.
3. Upload a new program logo / profile picture, refresh, and confirm it stays.
4. Redeploy once and confirm the images are still there.
5. For the **dual-approval evidence workflow**: complete the §6 staging test above before considering it production-ready.
