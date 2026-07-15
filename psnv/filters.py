import django_filters
from django import forms
from django.db.models import Q

from .models import (
    Anbieter,
    Einsatzgebiet,
    Oberbegriff,
    Spezialisierung,
    Versorgungsphase,
)


class AnbieterFilter(django_filters.FilterSet):
    """
    Drives the public search: category (Oberbegriff), specialization,
    Versorgungsphase, and free-text location (city / PLZ, looked up
    through Team -> Standort, since only Team carries a location).
    """

    name = django_filters.CharFilter(
        field_name="name", lookup_expr="icontains", label="Name / Stichwort",
    )
    oberbegriffe = django_filters.ModelMultipleChoiceFilter(
        queryset=Oberbegriff.objects.all(),
        label="Kategorie",
        widget=forms.CheckboxSelectMultiple,
    )
    spezialisierungen = django_filters.ModelMultipleChoiceFilter(
        queryset=Spezialisierung.objects.all(),
        label="Spezialisierung",
        widget=forms.CheckboxSelectMultiple,
    )
    versorgungsphasen = django_filters.ModelMultipleChoiceFilter(
        queryset=Versorgungsphase.objects.all(),
        label="Versorgungsphase",
        widget=forms.CheckboxSelectMultiple,
    )
    einsatzgebiete = django_filters.ModelMultipleChoiceFilter(
        queryset=Einsatzgebiet.objects.all(),
        label="Einsatzgebiet",
        widget=forms.CheckboxSelectMultiple,
    )
    ort = django_filters.CharFilter(
        method="filter_ort", label="Ort oder PLZ",
    )

    class Meta:
        model = Anbieter
        fields = ["name", "oberbegriffe", "spezialisierungen", "versorgungsphasen", "einsatzgebiete", "ort"]

    def filter_ort(self, queryset, name, value):
        return queryset.filter(
            Q(team__standort__city__icontains=value) | Q(team__standort__zip_code__icontains=value)
        )
