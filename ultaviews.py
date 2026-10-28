[1mdiff --git a/config/settings.py b/config/settings.py[m
[1mindex de8e5f4..e12ebd3 100644[m
[1m--- a/config/settings.py[m
[1m+++ b/config/settings.py[m
[36m@@ -29,8 +29,14 @@[m [mALLOWED_HOSTS = [[m
     if host.strip()[m
 ][m
 [m
[31m-if not DEBUG and not ALLOWED_HOSTS:[m
[31m-    ALLOWED_HOSTS = ["consulta-protocolo-dccf.onrender.com"][m
[32m+[m[32mif not DEBUG:[m
[32m+[m[32m    ALLOWED_HOSTS = list(set([m
[32m+[m[32m        ALLOWED_HOSTS + [[m
[32m+[m[32m            "consulta-protocolo-dccf.onrender.com",[m
[32m+[m[32m            "127.0.0.1",[m
[32m+[m[32m            "localhost",[m
[32m+[m[32m        ][m
[32m+[m[32m    ))[m
 [m
 [m
 # Application definition[m
[1mdiff --git a/consulta/urls.py b/consulta/urls.py[m
[1mindex 3e7fbc1..fcfa64b 100644[m
[1m--- a/consulta/urls.py[m
[1m+++ b/consulta/urls.py[m
[36m@@ -3,6 +3,7 @@[m [mfrom django.urls import path[m
 from . import views[m
 [m
 urlpatterns = [[m
[32m+[m[32m    path("", views.inicio, name="inicio"),[m
     path([m
         "api/protocolos/<str:numero>/<uuid:codigo_consulta>/",[m
         views.consultar_protocolo,[m
[1mdiff --git a/consulta/views.py b/consulta/views.py[m
[1mindex e440d3d..7f348ea 100644[m
[1m--- a/consulta/views.py[m
[1m+++ b/consulta/views.py[m
[36m@@ -2,13 +2,16 @@[m
 import json[m
 import os[m
 import secrets[m
[31m-[m
[31m-from django.http import JsonResponse[m
[32m+[m[32mfrom django.conf import settings[m
[32m+[m[32mfrom django.http import HttpResponse[m
[32m+[m[32mfrom pathlib import Path[m
[32m+[m[32mfrom django.http import JsonResponse, HttpResponse[m
 from django.utils.dateparse import parse_datetime[m
 from django.views.decorators.csrf import csrf_exempt[m
 [m
 from .models import ProtocoloPublico[m
 [m
[32m+[m[32mfrom django.shortcuts import render[m
 [m
 def consultar_protocolo(request, numero, codigo_consulta):[m
     try:[m
[36m@@ -29,7 +32,8 @@[m [mdef consultar_protocolo(request, numero, codigo_consulta):[m
         "situacao": protocolo.situacao,[m
         "data_atualizacao": protocolo.data_atualizacao.isoformat(),[m
     })[m
[31m-[m
[32m+[m[32mdef inicio(request):[m
[32m+[m[32m    return render(request, "consulta/index.html")[m
 [m
 @csrf_exempt[m
 def sincronizar_protocolo(request):[m
