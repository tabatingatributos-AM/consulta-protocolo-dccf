
from django.urls import path
from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path(
        "api/protocolos/<str:numero>/<uuid:codigo_consulta>/",
        views.consultar_protocolo,
        name="consultar_protocolo",
    ),
    path(
        "api/sincronizar/",
        views.sincronizar_protocolo,
        name="sincronizar_protocolo",
    ),
]
