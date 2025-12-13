# Eventify/Projeto/Projeto/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('aulaweb.urls')),  # URLs da aplicação web
    path('api/', include('aulaweb.api_urls')),  # URLs da API REST
]

# Adicionar isto para servir imagens no modo DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)