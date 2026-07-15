"""
Seeds the database with fake-but-realistic PSNV-Angebote so you can click
through search/filter/detail/admin without waiting for the real survey
import. Every value is invented - none of this is real contact data.

Usage:
    python manage.py seed_lookup_data   # if you haven't already
    python manage.py seed_fake_data

Re-running is safe: uses get_or_create/unique names throughout, so it
won't create duplicates on a second run.
"""

import random
from datetime import date

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from psnv.models import (
    Akteur,
    AkteurOrganisation,
    Anbieter,
    Einsatzgebiet,
    Einwilligung,
    Oberbegriff,
    Organisation,
    OrganisationStandort,
    Qualifikation,
    Spezialisierung,
    Sprache,
    Standort,
    Stelle,
    Team,
    Versorgungsphase,
    Zielgruppe,
)

random.seed(42)  # reproducible output across runs

CITIES = [
    # (city, zip_code, region, state, lat, lng)
    ("Wuppertal", "42119", "Bergisches Land", "Nordrhein-Westfalen", 51.2562, 7.1508),
    ("Köln", "50667", "Rheinland", "Nordrhein-Westfalen", 50.9375, 6.9603),
    ("Düsseldorf", "40213", "Rheinland", "Nordrhein-Westfalen", 51.2277, 6.7735),
    ("Essen", "45127", "Ruhrgebiet", "Nordrhein-Westfalen", 51.4556, 7.0116),
    ("Dortmund", "44135", "Ruhrgebiet", "Nordrhein-Westfalen", 51.5136, 7.4653),
    ("Bonn", "53111", "Rheinland", "Nordrhein-Westfalen", 50.7374, 7.0982),
    ("Aachen", "52062", "Rheinland", "Nordrhein-Westfalen", 50.7753, 6.0839),
    ("Bielefeld", "33602", "Ostwestfalen-Lippe", "Nordrhein-Westfalen", 52.0302, 8.5325),
    ("Münster", "48143", "Münsterland", "Nordrhein-Westfalen", 51.9607, 7.6261),
    ("Duisburg", "47051", "Ruhrgebiet", "Nordrhein-Westfalen", 51.4344, 6.7623),
]

SPRACHEN = [
    ("de", "Deutsch"), ("en", "Englisch"), ("tr", "Türkisch"),
    ("ar", "Arabisch"), ("ru", "Russisch"), ("pl", "Polnisch"),
]

SPEZIALISIERUNGEN = [
    "Kinder und Jugendliche", "Seenotrettung", "Interkulturelle Kompetenz",
    "Geflüchtete", "Sucht", "Ältere Menschen",
]

EINSATZGEBIETE = [
    ("NRW-weit", "Nordrhein-Westfalen"),
    ("Bergisches Land", "Bergisches Land"),
    ("Ruhrgebiet", "Ruhrgebiet"),
    ("Rheinland", "Rheinland"),
    ("Münsterland", "Münsterland"),
    ("Bundesweit", "Deutschland"),
]

STELLEN = ["Leitung", "Koordination", "Stellvertretende Leitung"]

ORGANISATIONEN = [
    ("DRK Kreisverband Wuppertal", ""),
    ("Johanniter-Unfall-Hilfe Köln", ""),
    ("Malteser Hilfsdienst Düsseldorf", ""),
    ("ASB Regionalverband Ruhr", ""),
]

# (name, typ, city_index, oberbegriffe[], spez[], phasen[], gebiete[], quals[], sprachen[], status)
FAKE_ANBIETER = [
    ("Kriseninterventionsteam Wuppertal", "team", 0,
     ["Kriseninterventionsteams (KIT)"], ["Kinder und Jugendliche"],
     ["Akutversorgung"], ["Bergisches Land"],
     ["Allgemeine PSNV Fachausbildung (PSNV-B & PSNV-E)"], ["de", "en"], "approved"),
    ("Notfallseelsorge Köln", "team", 1,
     ["Notfallseelsorge"], [], ["Akutversorgung"], ["Rheinland"],
     ["Notfallseelsorge Ausbildung (PSNV-B)"], ["de"], "approved"),
    ("Traumaambulanz Düsseldorf", "team", 2,
     ["Traumaambulanz"], ["Kinder und Jugendliche"], ["Regelversorgung"], ["Rheinland"],
     [], ["de", "tr"], "approved"),
    ("PSU-Team Feuerwehr Essen", "team", 3,
     ["PSNV-E Team", "Feuerwehr"], [], ["Akutversorgung"], ["Ruhrgebiet"],
     ["Psychosoziale Unterstützung (PSU) (PSNV-E)"], ["de"], "approved"),
    ("Telefonseelsorge Dortmund", "team", 4,
     ["Telefonseelsorge"], ["Sucht"], ["Prävention", "Akutversorgung"], ["Ruhrgebiet"],
     [], ["de", "ru", "pl"], "approved"),
    ("Schulpsychologischer Dienst Bonn", "team", 5,
     ["Schulpsycholog:in & Schulsozialarbeiter:in"], ["Kinder und Jugendliche"],
     ["Prävention"], ["Rheinland"], [], ["de"], "approved"),
    ("Migrationsberatung Aachen", "team", 6,
     ["Migrations- und Integrationsdienste"], ["Geflüchtete", "Interkulturelle Kompetenz"],
     ["Regelversorgung"], ["Rheinland"], [], ["de", "ar", "tr"], "approved"),
    ("Opferhilfestelle Bielefeld", "team", 7,
     ["Opferhilfestelle (LVR)"], [], ["Regelversorgung"], ["NRW-weit"],
     [], ["de"], "pending"),
    ("Traumapädagogik Münster", "akteur", 8,
     ["Traumapädagog:in/Traumafachberater:in"], ["Kinder und Jugendliche"],
     ["Regelversorgung"], ["Münsterland"], [], ["de", "en"], "approved"),
    ("Notfallpsychologie Duisburg", "akteur", 9,
     ["Notfallpsycholog:in"], ["Sucht"], ["Akutversorgung"], ["Ruhrgebiet"],
     [], ["de"], "approved"),
    ("Krisenintervention THW Wuppertal", "team", 0,
     ["Technisches Hilfswerk (THW)", "PSNV-B Team"], [], ["Akutversorgung"],
     ["Bergisches Land"], ["Krisenintervention Ausbildung (PSNV-B)"], ["de"], "approved"),
    ("Trauerbegleitung Köln", "akteur", 1,
     ["Trauerbegleiter:in"], ["Ältere Menschen"], ["Regelversorgung"], ["Rheinland"],
     [], ["de"], "pending"),
    ("Psychiatrische Institutsambulanz Düsseldorf", "team", 2,
     ["Psychiatrische Ambulanz (PIA)"], [], ["Regelversorgung"], ["Rheinland"],
     [], ["de"], "approved"),
    ("Bürgertelefon Krisenhotline Essen", "team", 3,
     ["Bürgertelefon/Krisenhotlines"], [], ["Prävention"], ["Ruhrgebiet"],
     [], ["de", "en"], "approved"),
    ("Familienberatungsstelle Dortmund", "team", 4,
     ["Erziehungs- und Familienberatungsstellen (EFB)"], ["Kinder und Jugendliche"],
     ["Regelversorgung"], ["Ruhrgebiet"], [], ["de", "pl"], "approved"),
    ("Obdachlosenhilfe Bonn", "team", 5,
     ["Obdachlosenhilfe"], [], ["Regelversorgung"], ["Rheinland"],
     [], ["de"], "pending"),
]


class Command(BaseCommand):
    help = "Seeds fake PSNV-Angebote (Akteure/Teams) for manual UI testing."

    def handle(self, *args, **options):
        user, _ = User.objects.get_or_create(
            username="demo_einreicher", defaults={"email": "demo@example.com"}
        )

        # --- lookup data this command needs beyond seed_lookup_data ------
        sprachen = {}
        for iso, name in SPRACHEN:
            obj, _ = Sprache.objects.get_or_create(iso_code=iso, defaults={"name": name})
            sprachen[iso] = obj

        spezialisierungen = {}
        for name in SPEZIALISIERUNGEN:
            obj, _ = Spezialisierung.objects.get_or_create(name=name)
            spezialisierungen[name] = obj

        einsatzgebiete = {}
        for name, region in EINSATZGEBIETE:
            obj, _ = Einsatzgebiet.objects.get_or_create(name=name, defaults={"region": region})
            einsatzgebiete[name] = obj

        for name in STELLEN:
            Stelle.objects.get_or_create(name=name)

        organisationen = []
        for name, _bos in ORGANISATIONEN:
            obj, _ = Organisation.objects.get_or_create(name=name)
            organisationen.append(obj)

        standorte = {}
        for i, (city, zip_code, region, state, lat, lng) in enumerate(CITIES):
            standort, _ = Standort.objects.get_or_create(
                city=city, zip_code=zip_code,
                defaults=dict(
                    street="Musterstraße", house_number=str(i + 1), region=region,
                    state=state, latitude=lat, longitude=lng, location_type="stationaer",
                ),
            )
            standorte[i] = standort
            # link every other city to one of the demo Organisationen
            if i % 2 == 0 and organisationen:
                OrganisationStandort.objects.get_or_create(
                    organisation=organisationen[(i // 2) % len(organisationen)], standort=standort,
                )

        oberbegriffe_cache = {o.name: o for o in Oberbegriff.objects.all()}
        phasen_cache = {p.name: p for p in Versorgungsphase.objects.all()}
        quals_cache = {q.name: q for q in Qualifikation.objects.all()}

        if not oberbegriffe_cache or not phasen_cache:
            self.stdout.write(self.style.WARNING(
                "Oberbegriff/Versorgungsphase tables are empty - run "
                "'python manage.py seed_lookup_data' first."
            ))
            return

        created_count = 0
        for (name, typ, city_idx, ober_names, spez_names, phase_names,
             gebiet_names, qual_names, sprache_isos, status) in FAKE_ANBIETER:

            if Anbieter.objects.filter(name=name).exists():
                continue  # already seeded

            shared_kwargs = dict(
                name=name,
                email=f"{name.lower().replace(' ', '.').replace(':', '')}@beispiel-psnv.de",
                phone_main=f"0{random.randint(200,299)}-{random.randint(100000,999999)}",
                website=f"https://www.beispiel-psnv.de/{name.lower().replace(' ', '-')}",
                status=status,
                verified=(status == "approved"),
                eingereicht_von=user,
            )

            if typ == "team":
                anbieter = Team.objects.create(
                    typ=Anbieter.Typ.TEAM, standort=standorte[city_idx], **shared_kwargs,
                )
            else:
                anbieter = Akteur.objects.create(typ=Anbieter.Typ.AKTEUR, **shared_kwargs)
                # give a couple of Akteure an Organisation membership too
                if organisationen and random.random() < 0.5:
                    AkteurOrganisation.objects.get_or_create(
                        akteur=anbieter, organisation=random.choice(organisationen),
                    )

            for n in ober_names:
                if n in oberbegriffe_cache:
                    anbieter.oberbegriffe.add(oberbegriffe_cache[n])
            for n in spez_names:
                anbieter.spezialisierungen.add(spezialisierungen[n])
            for n in phase_names:
                if n in phasen_cache:
                    anbieter.versorgungsphasen.add(phasen_cache[n])
            for n in gebiet_names:
                anbieter.einsatzgebiete.add(einsatzgebiete[n])
            for n in qual_names:
                if n in quals_cache:
                    anbieter.qualifikationen.add(quals_cache[n])
            for iso in sprache_isos:
                anbieter.sprachen.add(sprachen[iso])

            Einwilligung.objects.create(
                anbieter=anbieter, umfrage=True,
                aki_sichtbarkeit=(status == "approved"), consent_date=date.today(),
            )

            created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done. {created_count} new Anbieter created "
            f"({Anbieter.objects.filter(status='approved').count()} approved, "
            f"{Anbieter.objects.filter(status='pending').count()} pending)."
        ))
