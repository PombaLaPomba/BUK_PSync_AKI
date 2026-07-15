from django.urls import path

from . import views

app_name = "psnv"

urlpatterns = [
    path("", views.SucheView.as_view(), name="suche"),
    path("anbieter/<int:pk>/", views.AnbieterDetailView.as_view(), name="anbieter_detail"),
    path("einreichen/", views.EinreichenChoiceView.as_view(), name="einreichen"),
    path("einreichen/einzelperson/", views.AkteurSubmitView.as_view(), name="einreichen_akteur"),
    path("einreichen/team/", views.TeamSubmitView.as_view(), name="einreichen_team"),
    path("einreichen/danke/", views.EinreichenDankeView.as_view(), name="einreichen_danke"),
]
