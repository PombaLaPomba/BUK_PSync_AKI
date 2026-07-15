"""
One-time import of the AP1-3 survey export into the app's tables.

This is a STARTING POINT, not a finished importer: the exact column
names depend on how the survey tool exports (CSV/XLSX column headers
will not match these placeholders 1:1). Fill in the TODOs against your
actual export file, using PSNV_Frage_Tabelle_Mapping.xlsx as the map
from survey question -> model/field.

Usage (once finished):
    python manage.py import_survey path/to/export.csv

Re-running is NOT idempotent by default - this is meant to run once
against the final export. Add a dedupe check (e.g. on email) if you
expect to run it more than once.
"""

import csv

from django.core.management.base import BaseCommand, CommandError

from psnv.models import Akteur, Anbieter, Einwilligung, Standort, Team


class Command(BaseCommand):
    help = "One-time import of the closed AP1-3 survey export."

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str)
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Parse and report row counts without writing to the database.",
        )

    def handle(self, *args, **options):
        path = options["csv_path"]
        dry_run = options["dry_run"]

        try:
            f = open(path, newline="", encoding="utf-8")
        except FileNotFoundError as exc:
            raise CommandError(f"File not found: {path}") from exc

        with f:
            reader = csv.DictReader(f)
            rows_seen = 0
            rows_imported = 0

            for row in reader:
                rows_seen += 1

                # --- 1.1: struktur_typ decides Akteur vs Team ------------
                # TODO: replace "Wie ist Ihr PSNV-Angebot strukturiert?"
                # with the actual export column name.
                struktur = row.get("Wie ist Ihr PSNV-Angebot strukturiert?", "")
                is_team = "Team" in struktur or "Organisation" in struktur

                if dry_run:
                    continue

                # --- 1.6: Standort, only needed for Team rows -------------
                standort = None
                if is_team:
                    standort = Standort.objects.create(
                        street=row.get("Straße, Hausnummer", ""),  # TODO column name
                        zip_code=row.get("Postleitzahl", ""),      # TODO column name
                        city=row.get("Ort", ""),                    # TODO column name
                    )

                # --- 1.0 / 1.5a: base Anbieter fields ---------------------
                shared_kwargs = dict(
                    name=row.get("PSNV-Angebot Beschreibung", "")[:255],  # TODO column name
                    email=row.get("E-Mail", ""),                          # TODO column name
                    phone_main=row.get("Telefonnummer 1", ""),            # TODO column name
                    phone_secondary=row.get("Telefonnummer 2", ""),       # TODO column name
                    website=row.get("Website (URL)", ""),                 # TODO column name
                    status=Anbieter.Status.APPROVED,  # survey respondents are pre-vetted
                    verified=True,
                )

                if is_team:
                    anbieter = Team.objects.create(
                        typ=Anbieter.Typ.TEAM, standort=standort, **shared_kwargs,
                    )
                else:
                    anbieter = Akteur.objects.create(typ=Anbieter.Typ.AKTEUR, **shared_kwargs)

                # --- Datenschutz consent (DS-1 / DS-2) --------------------
                Einwilligung.objects.create(
                    anbieter=anbieter,
                    umfrage=True,
                    aki_sichtbarkeit=True,  # only True if the AKI-visibility checkbox was ticked
                )

                # TODO: attach M2M tags (Oberbegriff, Spezialisierung,
                # Versorgungsphase, Einsatzgebiet, Qualifikation, Sprache)
                # per PSNV_Frage_Tabelle_Mapping.xlsx, e.g.:
                #
                # for name in row.get("Oberbegriffe", "").split(","):
                #     name = name.strip()
                #     if name:
                #         ober, _ = Oberbegriff.objects.get_or_create(name=name)
                #         anbieter.oberbegriffe.add(ober)

                rows_imported += 1

        self.stdout.write(self.style.SUCCESS(
            f"Rows seen: {rows_seen}. Imported: {rows_imported}."
            + (" (dry run, nothing written)" if dry_run else "")
        ))
