from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Akteur, Standort, Team

# Fields every submitted Anbieter shares, regardless of subtype.
# "typ", "verified", "status", "eingereicht_von" are set by the view,
# not exposed to the person submitting the form.
SHARED_ANBIETER_FIELDS = [
    "name", "email", "phone_main", "phone_secondary", "website",
    "sprachen", "stellen", "versorgungsphasen", "spezialisierungen",
    "operative_psnv", "angebote", "einsatzgebiete", "qualifikationen",
    "oberbegriffe",
]

MULTISELECT_WIDGET = forms.CheckboxSelectMultiple


class AkteurForm(forms.ModelForm):
    class Meta:
        model = Akteur
        fields = SHARED_ANBIETER_FIELDS
        widgets = {
            "sprachen": MULTISELECT_WIDGET,
            "stellen": MULTISELECT_WIDGET,
            "versorgungsphasen": MULTISELECT_WIDGET,
            "spezialisierungen": MULTISELECT_WIDGET,
            "operative_psnv": MULTISELECT_WIDGET,
            "angebote": MULTISELECT_WIDGET,
            "einsatzgebiete": MULTISELECT_WIDGET,
            "qualifikationen": MULTISELECT_WIDGET,
            "oberbegriffe": MULTISELECT_WIDGET,
        }


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = SHARED_ANBIETER_FIELDS  # "standort" is attached separately in the view
        widgets = AkteurForm.Meta.widgets


class StandortForm(forms.ModelForm):
    class Meta:
        model = Standort
        fields = ["street", "house_number", "zip_code", "city", "region", "state", "location_type"]


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
