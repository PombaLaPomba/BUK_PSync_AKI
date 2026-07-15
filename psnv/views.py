from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, TemplateView
from django_filters.views import FilterView

from .filters import AnbieterFilter
from .forms import AkteurForm, SignUpForm, StandortForm, TeamForm
from .models import Akteur, Anbieter


class SucheView(FilterView):
    """Public search. Only entries a staff member has approved are shown."""

    model = Anbieter
    filterset_class = AnbieterFilter
    template_name = "psnv/suche.html"
    context_object_name = "anbieter_liste"
    paginate_by = 20

    def get_queryset(self):
        return (
            Anbieter.objects.filter(status=Anbieter.Status.APPROVED, verified=True)
            .select_related("team__standort")
            .prefetch_related("oberbegriffe", "spezialisierungen", "versorgungsphasen")
            .order_by("name")
        )


class AnbieterDetailView(DetailView):
    model = Anbieter
    template_name = "psnv/anbieter_detail.html"
    context_object_name = "anbieter"
    pk_url_kwarg = "pk"

    def get_queryset(self):
        qs = Anbieter.objects.all()
        if not self.request.user.is_staff:
            qs = qs.filter(status=Anbieter.Status.APPROVED, verified=True)
        return qs


class EinreichenChoiceView(LoginRequiredMixin, TemplateView):
    """Landing page: 'submit as individual' vs 'submit as team'."""

    template_name = "psnv/einreichen_choice.html"


class AkteurSubmitView(LoginRequiredMixin, CreateView):
    model = Akteur
    form_class = AkteurForm
    template_name = "psnv/einreichen_form.html"
    success_url = reverse_lazy("psnv:einreichen_danke")

    def form_valid(self, form):
        form.instance.typ = Anbieter.Typ.AKTEUR
        form.instance.status = Anbieter.Status.PENDING
        form.instance.verified = False
        form.instance.eingereicht_von = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titel"] = "PSNV-Angebot als Einzelperson einreichen"
        return ctx


class TeamSubmitView(LoginRequiredMixin, TemplateView):
    """
    Team submission needs two forms saved together: the Standort, then
    the Team itself (which requires standort_id to already exist).
    """

    template_name = "psnv/einreichen_team_form.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {
            "team_form": TeamForm(),
            "standort_form": StandortForm(),
            "titel": "PSNV-Angebot als Team einreichen",
        })

    def post(self, request, *args, **kwargs):
        team_form = TeamForm(request.POST)
        standort_form = StandortForm(request.POST)

        if team_form.is_valid() and standort_form.is_valid():
            standort = standort_form.save()

            team = team_form.save(commit=False)
            team.standort = standort
            team.typ = Anbieter.Typ.TEAM
            team.status = Anbieter.Status.PENDING
            team.verified = False
            team.eingereicht_von = request.user
            team.save()
            team_form.save_m2m()

            return redirect("psnv:einreichen_danke")

        return render(request, self.template_name, {
            "team_form": team_form,
            "standort_form": standort_form,
            "titel": "PSNV-Angebot als Team einreichen",
        })


class EinreichenDankeView(TemplateView):
    template_name = "psnv/einreichen_danke.html"


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Konto erstellt. Bitte melden Sie sich an.")
        return response
