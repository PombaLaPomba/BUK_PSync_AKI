"""
Models for the PSNV / AKI directory.

Mirrors Final_DBdiagram.txt as closely as Django allows:

- Anbieter is the supertype. Akteur and Team are implemented with Django's
  multi-table inheritance, which gives them a OneToOneField primary key
  back to Anbieter automatically - exactly the "akteur_id = anbieter_id"
  pattern from the diagram.
- Lookup/tag tables (Sprache, Stelle, Versorgungsphase, Spezialisierung,
  Zielgruppe, Operative_PSNV, Oberbegriff, Einsatzgebiet, Qualifikation)
  are plain models attached to Anbieter via ManyToManyField.
- Pure junction tables with no extra columns use Django's default M2M
  table. Junction tables that carry extra data (e.g. anbieter_qualifikation
  .aggregated) get an explicit "through" model.
- Anbieter.status / verified drive the moderation workflow: new
  submissions come in as PENDING and are not shown in search results
  until a staff member approves them.
"""

from django.conf import settings
from django.db import models


# ===========================================================================
# CORE ENTITIES
# ===========================================================================

class Anbieter(models.Model):
    """Supertype: anything findable/contactable through the search."""

    class Typ(models.TextChoices):
        AKTEUR = "akteur", "Einzelperson (Akteur)"
        TEAM = "team", "Team / Organisationseinheit"

    class Status(models.TextChoices):
        PENDING = "pending", "Ausstehend (wartet auf Freigabe)"
        APPROVED = "approved", "Freigegeben"
        REJECTED = "rejected", "Abgelehnt"

    anbieter_id = models.AutoField(primary_key=True)
    typ = models.CharField(max_length=10, choices=Typ.choices)
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    phone_main = models.CharField("Telefon 1", max_length=50, blank=True)
    phone_secondary = models.CharField("Telefon 2", max_length=50, blank=True)
    website = models.URLField(blank=True)
    verified = models.BooleanField(default=False)
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # who submitted this entry through the app (null for the one-time survey import)
    eingereicht_von = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="eingereichte_anbieter",
    )

    # --- M2M tag/capability relations ---
    sprachen = models.ManyToManyField("Sprache", through="AnbieterSprache", blank=True, related_name="anbieter")
    stellen = models.ManyToManyField("Stelle", through="AnbieterStelle", blank=True, related_name="anbieter")
    versorgungsphasen = models.ManyToManyField("Versorgungsphase", through="AnbieterPhase", blank=True, related_name="anbieter")
    spezialisierungen = models.ManyToManyField("Spezialisierung", through="AnbieterSpezialisierung", blank=True, related_name="anbieter")
    operative_psnv = models.ManyToManyField("OperativePSNV", through="AnbieterOperative", blank=True, related_name="anbieter")
    angebote = models.ManyToManyField("PSNVAngebot", through="AnbieterAngebot", blank=True, related_name="anbieter")
    einsatzgebiete = models.ManyToManyField("Einsatzgebiet", through="AnbieterEinsatzgebiet", blank=True, related_name="anbieter")
    qualifikationen = models.ManyToManyField("Qualifikation", through="AnbieterQualifikation", blank=True, related_name="anbieter")
    oberbegriffe = models.ManyToManyField("Oberbegriff", through="AnbieterOberbegriff", blank=True, related_name="anbieter")

    class Meta:
        db_table = "anbieter"
        indexes = [models.Index(fields=["name"])]
        verbose_name = "Anbieter"
        verbose_name_plural = "Anbieter"

    def __str__(self):
        return self.name


class Akteur(Anbieter):
    """Subtype: a single person."""

    teams = models.ManyToManyField("Team", through="AkteurTeam", blank=True, related_name="mitglieder")
    organisationen = models.ManyToManyField("Organisation", through="AkteurOrganisation", blank=True, related_name="mitglieder")

    class Meta:
        db_table = "akteur"
        verbose_name = "Akteur (Einzelperson)"
        verbose_name_plural = "Akteure (Einzelpersonen)"


class Team(Anbieter):
    """Subtype: a team / organisational unit, tied to a location."""

    standort = models.ForeignKey("Standort", on_delete=models.PROTECT, related_name="teams")

    class Meta:
        db_table = "team"
        verbose_name = "Team"
        verbose_name_plural = "Teams"


class Standort(models.Model):
    class LocationType(models.TextChoices):
        STATIONAER = "stationaer", "Stationär / standortgebunden"
        REGIONAL = "regional", "Regional"
        BUNDESWEIT = "bundesweit", "Bundesweit"
        ANDERE = "andere", "Andere"

    standort_id = models.AutoField(primary_key=True)
    street = models.CharField("Straße", max_length=255, blank=True)
    house_number = models.CharField("Hausnummer", max_length=20, blank=True)
    zip_code = models.CharField("PLZ", max_length=10, blank=True)
    city = models.CharField("Ort", max_length=255, blank=True)
    region = models.CharField(max_length=255, blank=True)
    state = models.CharField("Bundesland", max_length=255, blank=True)
    country = models.CharField(max_length=100, default="Germany")
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    location_type = models.CharField(max_length=20, choices=LocationType.choices, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    organisationen = models.ManyToManyField("Organisation", through="OrganisationStandort", blank=True, related_name="standorte")

    class Meta:
        db_table = "standort"
        indexes = [models.Index(fields=["region", "state", "latitude", "longitude"])]
        verbose_name = "Standort"
        verbose_name_plural = "Standorte"

    def __str__(self):
        parts = [p for p in [self.street, self.zip_code, self.city] if p]
        return ", ".join(parts) or f"Standort {self.standort_id}"


class Organisation(models.Model):
    class BosKategorie(models.TextChoices):
        POLIZEI = "Polizei", "Polizei"
        FEUERWEHR = "Feuerwehr", "Feuerwehr"
        THW = "THW", "THW"
        SONSTIGE = "BOS-Sonstige", "BOS - Sonstige"

    organisation_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    bos_kategorie = models.CharField(max_length=20, choices=BosKategorie.choices, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "organisation"
        verbose_name = "Organisation"
        verbose_name_plural = "Organisationen"

    def __str__(self):
        return self.name


class OrganisationStandort(models.Model):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    standort = models.ForeignKey(Standort, on_delete=models.CASCADE)

    class Meta:
        db_table = "organisation_standort"
        unique_together = ("organisation", "standort")


# ===========================================================================
# TAG / CAPABILITY LOOKUP TABLES
# ===========================================================================

class Sprache(models.Model):
    sprache_id = models.AutoField(primary_key=True)
    iso_code = models.CharField(max_length=10, blank=True)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "sprache"
        verbose_name_plural = "Sprachen"

    def __str__(self):
        return self.name


class Stelle(models.Model):
    stelle_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)  # z.B. "Leitung", "Koordinator"

    class Meta:
        db_table = "stelle"
        verbose_name_plural = "Stellen"

    def __str__(self):
        return self.name


class Versorgungsphase(models.Model):
    phase_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)  # Prävention / Akutversorgung / Regelversorgung

    class Meta:
        db_table = "versorgungsphase"
        verbose_name_plural = "Versorgungsphasen"

    def __str__(self):
        return self.name


class Spezialisierung(models.Model):
    spez_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    zielgruppen = models.ManyToManyField("Zielgruppe", through="SpezZielgruppe", blank=True, related_name="spezialisierungen")

    class Meta:
        db_table = "spezialisierung"
        verbose_name_plural = "Spezialisierungen"

    def __str__(self):
        return self.name


class Zielgruppe(models.Model):
    ziel_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    intern_nur = models.BooleanField(default=False)
    extern_nur = models.BooleanField(default=False)
    individuelle_betreuung = models.BooleanField(default=False)

    class Meta:
        db_table = "zielgruppe"
        verbose_name_plural = "Zielgruppen"

    def __str__(self):
        return self.name


class OperativePSNV(models.Model):
    operative_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = "operative_psnv"
        verbose_name = "Operative PSNV"
        verbose_name_plural = "Operative PSNV"

    def __str__(self):
        return self.name


class Oberbegriff(models.Model):
    ober_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "oberbegriff"
        verbose_name_plural = "Oberbegriffe"

    def __str__(self):
        return self.name


class Einsatzgebiet(models.Model):
    gebiet_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    region = models.CharField(max_length=255, blank=True)
    geometry = models.TextField(blank=True, help_text="GeoJSON, falls vorhanden")

    class Meta:
        db_table = "einsatzgebiet"
        verbose_name_plural = "Einsatzgebiete"

    def __str__(self):
        return self.name


class Qualifikation(models.Model):
    qual_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "qualifikation"
        verbose_name_plural = "Qualifikationen"

    def __str__(self):
        return self.name


class PSNVAngebot(models.Model):
    class DienstTyp(models.TextChoices):
        BERATUNG = "Psychosoziale_Beratung", "Psychosoziale Beratung"
        SOZIALE_DIENSTE = "Soziale_Dienste", "Soziale Dienste"

    class ArtBetreuung(models.TextChoices):
        KLINISCH = "Klinisch", "Klinisch"
        PSYCHOTHERAPEUTISCH = "Psychotherapeutisch", "Psychotherapeutisch"

    class Liefermodus(models.TextChoices):
        INTERN = "intern", "Intern (nur eigene Organisation)"
        EXTERN = "extern", "Extern (für alle registrierten AKI-Akteure sichtbar)"
        BEIDES = "intern und extern", "Intern und extern"

    angebot_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    dienst_typ = models.CharField(max_length=30, choices=DienstTyp.choices, blank=True)
    art_betreuung = models.CharField(max_length=30, choices=ArtBetreuung.choices, blank=True)
    liefermodus = models.CharField(max_length=20, choices=Liefermodus.choices, blank=True)

    class Meta:
        db_table = "psnv_angebot"
        verbose_name = "PSNV-Angebot"
        verbose_name_plural = "PSNV-Angebote"

    def __str__(self):
        return self.name


# ===========================================================================
# M2M JUNCTION TABLES (plain - no extra columns beyond the two FKs)
# ===========================================================================

class AnbieterSprache(models.Model):
    anbieter = models.ForeignKey(Anbieter, on_delete=models.CASCADE)
    sprache = models.ForeignKey(Sprache, on_delete=models.CASCADE)

    class Meta:
        db_table = "anbieter_sprache"
        unique_together = ("anbieter", "sprache")


class AnbieterStelle(models.Model):
    anbieter = models.ForeignKey(Anbieter, on_delete=models.CASCADE)
    stelle = models.ForeignKey(Stelle, on_delete=models.CASCADE)

    class Meta:
        db_table = "anbieter_stelle"
        unique_together = ("anbieter", "stelle")


class AnbieterPhase(models.Model):
    anbieter = models.ForeignKey(Anbieter, on_delete=models.CASCADE)
    phase = models.ForeignKey(Versorgungsphase, on_delete=models.CASCADE)

    class Meta:
        db_table = "anbieter_phase"
        unique_together = ("anbieter", "phase")


class AnbieterSpezialisierung(models.Model):
    anbieter = models.ForeignKey(Anbieter, on_delete=models.CASCADE)
    spez = models.ForeignKey(Spezialisierung, on_delete=models.CASCADE)

    class Meta:
        db_table = "anbieter_spezialisierung"
        unique_together = ("anbieter", "spez")


class SpezZielgruppe(models.Model):
    spez = models.ForeignKey(Spezialisierung, on_delete=models.CASCADE)
    ziel = models.ForeignKey(Zielgruppe, on_delete=models.CASCADE)

    class Meta:
        db_table = "spez_zielgruppe"
        unique_together = ("spez", "ziel")


class AnbieterOperative(models.Model):
    anbieter = models.ForeignKey(Anbieter, on_delete=models.CASCADE)
    operative = models.ForeignKey(OperativePSNV, on_delete=models.CASCADE)

    class Meta:
        db_table = "anbieter_operative"
        unique_together = ("anbieter", "operative")


class AnbieterAngebot(models.Model):
    anbieter = models.ForeignKey(Anbieter, on_delete=models.CASCADE)
    angebot = models.ForeignKey(PSNVAngebot, on_delete=models.CASCADE)

    class Meta:
        db_table = "anbieter_angebot"
        unique_together = ("anbieter", "angebot")


class AnbieterEinsatzgebiet(models.Model):
    anbieter = models.ForeignKey(Anbieter, on_delete=models.CASCADE)
    gebiet = models.ForeignKey(Einsatzgebiet, on_delete=models.CASCADE)

    class Meta:
        db_table = "anbieter_einsatzgebiet"
        unique_together = ("anbieter", "gebiet")


class AnbieterOberbegriff(models.Model):
    anbieter = models.ForeignKey(Anbieter, on_delete=models.CASCADE)
    ober = models.ForeignKey(Oberbegriff, on_delete=models.CASCADE)

    class Meta:
        db_table = "anbieter_oberbegriff"
        unique_together = ("anbieter", "ober")


class AkteurTeam(models.Model):
    akteur = models.ForeignKey(Akteur, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    class Meta:
        db_table = "akteur_team"
        unique_together = ("akteur", "team")


class AkteurOrganisation(models.Model):
    akteur = models.ForeignKey(Akteur, on_delete=models.CASCADE)
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)

    class Meta:
        db_table = "akteur_organisation"
        unique_together = ("akteur", "organisation")


# ===========================================================================
# M2M JUNCTION TABLE WITH EXTRA DATA
# ===========================================================================

class AnbieterQualifikation(models.Model):
    anbieter = models.ForeignKey(Anbieter, on_delete=models.CASCADE)
    qual = models.ForeignKey(Qualifikation, on_delete=models.CASCADE)
    aggregated = models.BooleanField(
        default=False,
        help_text="Angabe gilt aggregiert für das gesamte Team, nicht für eine Einzelperson",
    )

    class Meta:
        db_table = "anbieter_qualifikation"
        unique_together = ("anbieter", "qual")


# ===========================================================================
# 1:N FACHINFORMATIONEN (one Anbieter -> many rows)
# ===========================================================================

class Verfuegbarkeit(models.Model):
    verf_id = models.AutoField(primary_key=True)
    anbieter = models.ForeignKey(Anbieter, on_delete=models.CASCADE, related_name="verfuegbarkeiten")
    type = models.CharField(max_length=100)  # z.B. "24/7", "feste Wochentage", "saisonal"
    details = models.TextField(blank=True)

    class Meta:
        db_table = "verfuegbarkeit"
        verbose_name_plural = "Verfügbarkeiten"

    def __str__(self):
        return f"{self.anbieter} – {self.type}"


class AlarmKanal(models.Model):
    kanal_id = models.AutoField(primary_key=True)
    anbieter = models.ForeignKey(Anbieter, on_delete=models.CASCADE, related_name="alarm_kanaele")
    channel_type = models.CharField(max_length=100)  # z.B. "Leitstelle", "interne Struktur"
    description = models.TextField(blank=True)

    class Meta:
        db_table = "alarm_kanal"
        verbose_name = "Alarmierungskanal"
        verbose_name_plural = "Alarmierungskanäle"

    def __str__(self):
        return f"{self.anbieter} – {self.channel_type}"


class Finanzierung(models.Model):
    fin_id = models.AutoField(primary_key=True)
    anbieter = models.ForeignKey(Anbieter, on_delete=models.CASCADE, related_name="finanzierungen")
    form = models.CharField(max_length=255)  # z.B. "kostenfrei", "Kassenabrechnung"
    note = models.TextField(blank=True)

    class Meta:
        db_table = "finanzierung"
        verbose_name_plural = "Finanzierungen"

    def __str__(self):
        return f"{self.anbieter} – {self.form}"


class Einwilligung(models.Model):
    ein_id = models.AutoField(primary_key=True)
    anbieter = models.ForeignKey(Anbieter, on_delete=models.CASCADE, related_name="einwilligungen")
    umfrage = models.BooleanField(default=False, help_text="Einwilligung zur Umfrage-Teilnahme")
    aki_sichtbarkeit = models.BooleanField(default=False, help_text="Einwilligung zur Sichtbarkeit im AKI")
    consent_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "einwilligung"
        verbose_name_plural = "Einwilligungen"

    def __str__(self):
        return f"Einwilligung {self.anbieter} ({self.consent_date})"


class GrossschadenErfahrung(models.Model):
    erf_id = models.AutoField(primary_key=True)
    anbieter = models.ForeignKey(Anbieter, on_delete=models.CASCADE, related_name="grossschaden_erfahrungen")
    einsatz_anzahl = models.PositiveIntegerField(help_text="Anzahl Einsätze in Großschadenslagen")

    class Meta:
        db_table = "grossschaden_erfahrung"
        verbose_name = "Großschadenslagen-Erfahrung"
        verbose_name_plural = "Großschadenslagen-Erfahrungen"

    def __str__(self):
        return f"{self.anbieter} – {self.einsatz_anzahl} Einsätze"
