from django.contrib import admin

from . import models


# ---------------------------------------------------------------------------
# Lookup / tag tables - simple registration, used as autocomplete sources
# ---------------------------------------------------------------------------

@admin.register(models.Sprache)
class SpracheAdmin(admin.ModelAdmin):
    list_display = ("name", "iso_code")
    search_fields = ("name", "iso_code")


@admin.register(models.Stelle)
class StelleAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(models.Versorgungsphase)
class VersorgungsphaseAdmin(admin.ModelAdmin):
    list_display = ("name",)


class SpezZielgruppeInline(admin.TabularInline):
    model = models.SpezZielgruppe
    extra = 1


@admin.register(models.Spezialisierung)
class SpezialisierungAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    inlines = [SpezZielgruppeInline]


@admin.register(models.Zielgruppe)
class ZielgruppeAdmin(admin.ModelAdmin):
    list_display = ("name", "intern_nur", "extern_nur", "individuelle_betreuung")
    search_fields = ("name",)


@admin.register(models.OperativePSNV)
class OperativePSNVAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(models.Oberbegriff)
class OberbegriffAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(models.Einsatzgebiet)
class EinsatzgebietAdmin(admin.ModelAdmin):
    list_display = ("name", "region")
    search_fields = ("name", "region")


@admin.register(models.Qualifikation)
class QualifikationAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(models.PSNVAngebot)
class PSNVAngebotAdmin(admin.ModelAdmin):
    list_display = ("name", "dienst_typ", "art_betreuung", "liefermodus")
    search_fields = ("name",)


@admin.register(models.Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = ("name", "bos_kategorie")
    search_fields = ("name",)


@admin.register(models.Standort)
class StandortAdmin(admin.ModelAdmin):
    list_display = ("__str__", "region", "state", "location_type", "latitude", "longitude")
    search_fields = ("city", "zip_code", "region", "state")
    list_filter = ("location_type", "state")


# ---------------------------------------------------------------------------
# M2M "through" tables - inlined onto Akteur/Team so tags can be attached
# without leaving the provider's edit page
# ---------------------------------------------------------------------------

class AnbieterSpracheInline(admin.TabularInline):
    model = models.AnbieterSprache
    extra = 1


class AnbieterStelleInline(admin.TabularInline):
    model = models.AnbieterStelle
    extra = 1


class AnbieterPhaseInline(admin.TabularInline):
    model = models.AnbieterPhase
    extra = 1


class AnbieterSpezialisierungInline(admin.TabularInline):
    model = models.AnbieterSpezialisierung
    extra = 1


class AnbieterOperativeInline(admin.TabularInline):
    model = models.AnbieterOperative
    extra = 1


class AnbieterAngebotInline(admin.TabularInline):
    model = models.AnbieterAngebot
    extra = 1


class AnbieterEinsatzgebietInline(admin.TabularInline):
    model = models.AnbieterEinsatzgebiet
    extra = 1


class AnbieterQualifikationInline(admin.TabularInline):
    model = models.AnbieterQualifikation
    extra = 1


class AnbieterOberbegriffInline(admin.TabularInline):
    model = models.AnbieterOberbegriff
    extra = 1


class VerfuegbarkeitInline(admin.TabularInline):
    model = models.Verfuegbarkeit
    extra = 1


class AlarmKanalInline(admin.TabularInline):
    model = models.AlarmKanal
    extra = 1


class FinanzierungInline(admin.TabularInline):
    model = models.Finanzierung
    extra = 1


class EinwilligungInline(admin.TabularInline):
    model = models.Einwilligung
    extra = 1


class GrossschadenErfahrungInline(admin.TabularInline):
    model = models.GrossschadenErfahrung
    extra = 1


TAG_AND_FACHINFO_INLINES = [
    AnbieterOberbegriffInline,
    AnbieterSpezialisierungInline,
    AnbieterPhaseInline,
    AnbieterOperativeInline,
    AnbieterAngebotInline,
    AnbieterEinsatzgebietInline,
    AnbieterQualifikationInline,
    AnbieterSpracheInline,
    AnbieterStelleInline,
    VerfuegbarkeitInline,
    AlarmKanalInline,
    FinanzierungInline,
    EinwilligungInline,
    GrossschadenErfahrungInline,
]

ANBIETER_BASE_FIELDS = ("name", "typ", "status", "verified", "email", "phone_main", "phone_secondary", "website")


@admin.register(models.Akteur)
class AkteurAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "verified", "email")
    list_filter = ("status", "verified")
    search_fields = ("name", "email")
    readonly_fields = ("typ", "created_at", "updated_at")
    inlines = TAG_AND_FACHINFO_INLINES


@admin.register(models.Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "standort", "status", "verified", "email")
    list_filter = ("status", "verified")
    search_fields = ("name", "email", "standort__city", "standort__zip_code")
    readonly_fields = ("typ", "created_at", "updated_at")
    inlines = TAG_AND_FACHINFO_INLINES


@admin.action(description="Ausgewählte Anbieter freigeben (für AKI-Suche sichtbar machen)")
def freigeben(modeladmin, request, queryset):
    queryset.update(status=models.Anbieter.Status.APPROVED, verified=True)


@admin.action(description="Ausgewählte Anbieter ablehnen")
def ablehnen(modeladmin, request, queryset):
    queryset.update(status=models.Anbieter.Status.REJECTED, verified=False)


@admin.register(models.Anbieter)
class AnbieterAdmin(admin.ModelAdmin):
    """
    Read-oriented moderation queue across both subtypes. Use this to see
    everything pending approval; use the Akteur/Team admin pages above
    to actually edit an entry's tags and Fachinformationen.
    """

    list_display = ("name", "typ", "status", "verified", "eingereicht_von", "created_at")
    list_filter = ("status", "verified", "typ")
    search_fields = ("name", "email")
    actions = [freigeben, ablehnen]
    readonly_fields = [f.name for f in models.Anbieter._meta.fields]

    def has_add_permission(self, request):
        # New entries are created as Akteur or Team (via their own admin
        # pages or the public form), not directly as a bare Anbieter.
        return False
