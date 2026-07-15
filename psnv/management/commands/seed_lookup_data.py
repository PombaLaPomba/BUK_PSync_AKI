"""
Populates the fixed-catalogue lookup tables (Oberbegriff, Qualifikation,
Versorgungsphase, Zielgruppe, ...) with the options that were already
hard-coded into the survey (AP1-3 Umfrage, questions 1.4, 1.8, 2.0/3.2,
3.3). Run once after migrate:

    python manage.py seed_lookup_data

Safe to re-run: uses get_or_create throughout.
"""

from django.core.management.base import BaseCommand

from psnv.models import Oberbegriff, Qualifikation, Versorgungsphase, Zielgruppe

OBERBEGRIFFE = [
    # Behörden und Organisationen mit Sicherheitsaufgaben (BOS) - question 1.4
    "Bundeswehr", "Feuerwehr", "Hilfsorganisation", "Polizei", "Technisches Hilfswerk (THW)",
    # Operative PSNV & Akutversorgung
    "Kriseninterventionsteams (KIT)", "Notfallpsycholog:in", "Notfallseelsorge",
    "PSNV-B Team", "PSNV-E Team", "Psychosoziale Beratung & Soziale Dienste",
    "Traumapädagog:in/Traumafachberater:in", "Trauerbegleiter:in", "Telefonseelsorge",
    "Schulpsycholog:in & Schulsozialarbeiter:in", "Migrations- und Integrationsdienste",
    "Erziehungs- und Familienberatungsstellen (EFB)", "Bürgertelefon/Krisenhotlines",
    "Pfarrer:in", "Obdachlosenhilfe", "Behindertenhilfe", "Opferhilfestelle (LVR)",
    # Klinische & Psychotherapeutische Regelversorgung
    "Fachärzt:in für Psychiatrie und Psychotherapie", "Hausärzt:in",
    "Kinder- und Jugendpsychotherapeut:in", "Psychiatrische Ambulanz (PIA)",
    "Psychiatrische Klinik", "Psychosomatische Klinik", "Psychologische Psychotherapeut:in",
    "Traumaambulanz",
]

GRUNDAUSBILDUNGEN = [  # question 3.3
    "Allgemeine PSNV Fachausbildung (PSNV-B & PSNV-E)",
    "Krisenintervention Ausbildung (PSNV-B)",
    "Notfallseelsorge Ausbildung (PSNV-B)",
    "Stressbearbeitung nach belastenden Ereignissen (SbE) (PSNV-E)",
    "Critical Incident Stress Management (CISM) (PSNV-E)",
    "Psychosoziale Unterstützung (PSU) (PSNV-E)",
]

VERSORGUNGSPHASEN = ["Prävention", "Akutversorgung", "Regelversorgung"]  # question 1.8

ZIELGRUPPEN = ["Einsatzkräfte", "Betroffene"]  # questions 2.0 / 3.2


class Command(BaseCommand):
    help = "Seeds Oberbegriff/Qualifikation/Versorgungsphase/Zielgruppe from the survey catalogues."

    def handle(self, *args, **options):
        created = 0
        for name in OBERBEGRIFFE:
            _, was_created = Oberbegriff.objects.get_or_create(name=name)
            created += was_created

        for name in GRUNDAUSBILDUNGEN:
            _, was_created = Qualifikation.objects.get_or_create(name=name)
            created += was_created

        for name in VERSORGUNGSPHASEN:
            _, was_created = Versorgungsphase.objects.get_or_create(name=name)
            created += was_created

        for name in ZIELGRUPPEN:
            _, was_created = Zielgruppe.objects.get_or_create(name=name)
            created += was_created

        self.stdout.write(self.style.SUCCESS(f"Seed complete. {created} new lookup rows created."))
