# PSync – PSNV-Finder (Django backend)

Backend scaffold implementing `Final_DBdiagram.txt` 1:1 as Django models,
with a public filtered search, a login-gated submission form, and an
admin-based moderation queue.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py seed_lookup_data  # populates Oberbegriff/Qualifikation/Versorgungsphase/Zielgruppe
python manage.py createsuperuser
python manage.py runserver
```

Then:
- `http://127.0.0.1:8000/` — public search
- `http://127.0.0.1:8000/accounts/signup/` — register an account (needed to submit)
- `http://127.0.0.1:8000/admin/` — moderation queue (log in with the superuser)

## How the pieces map to your schema

- **`psnv/models.py`** — every table from `Final_DBdiagram.txt`. `Akteur`
  and `Team` use Django multi-table inheritance, which gives them a
  shared primary key with `Anbieter` automatically — the same pattern as
  `akteur_id = Anbieter.anbieter_id` in the diagram.
- Plain junction tables (no extra columns) are modeled explicitly with
  `db_table` set to match the diagram's names, rather than letting
  Django auto-generate an M2M table, so the DB you inspect matches the
  diagram you already reviewed.
- `anbieter_qualifikation.aggregated` is the one junction table with a
  real extra column, so it gets a proper `through=` model.

## Moderation workflow

`Anbieter.status` (`pending` / `approved` / `rejected`) and `verified`
gate visibility:
- New submissions via the public form always land as `pending`.
- Only `status=approved, verified=True` entries show up in search
  (`SucheView.get_queryset`) or are viewable by non-staff on the detail
  page.
- Staff approve/reject from the **Anbieter** list in `/admin/` (bulk
  actions), then edit tags/Fachinformationen from the **Akteur** or
  **Team** admin pages, which have inlines for every M2M and 1:N table.

## One-time survey import

`psnv/management/commands/import_survey.py` is a **starting skeleton**,
not a finished importer — the TODOs mark where you need to plug in your
actual export's column names. Cross-reference against
`PSNV_Frage_Tabelle_Mapping.xlsx` (the question → table mapping we built
earlier) while filling it in. Run with `--dry-run` first to sanity-check
row counts before writing to the database.

## Known gaps carried over from the schema/mapping discussion

These didn't have an obvious home in `Final_DBdiagram.txt` — decide how
you want to handle them before the survey import:

1. **Question 3.6** (up to 5 Großschadenslagen deployments with
   Ereignis/Ort/Zeitraum/Tätigkeit) — the diagram only has
   `Grossschaden_Erfahrung.einsatz_anzahl` (a count), not the deployment
   details. If you want those preserved, add a child table.
2. **Abschluss free-text feedback** — no field/table captures this.
   Low-stakes to skip if you don't need it for the app itself.
3. **Question 1.3** (intern/extern) currently has no explicit home —
   `Zielgruppe.intern_nur`/`extern_nur` live on the target-group lookup,
   not on `Anbieter`, which is conceptually a bit indirect.

## Next steps (not yet built)

- **Geocoding**: `Standort.latitude`/`longitude` are there but unused.
  A one-off management command using Nominatim/OSM (free, fits a
  research project) to backfill them from address fields, run after
  the survey import.
- **PostGIS migration**: swap the `DATABASES` block in `settings.py`
  (commented alternative already included) once you want real
  distance-based search instead of exact city/PLZ matching.
- **Styling**: templates are functional Bootstrap-via-CDN, not
  designed — fine for internal testing, worth a pass before anyone
  outside the team sees it.
