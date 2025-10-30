from django.contrib import admin
from django.urls import path
from ubicaciones import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.mapa_view, name='mapa'),  
]
