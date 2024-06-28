from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.documentation import include_docs_urls

urlpatterns = [
    path('oficinaAmbiente/', views.OficinaAmbienteList.as_view()),
    path('oficinaAmbiente/<int:pk>/', views.OficinaAmbienteDetail.as_view()),
    path('docs/', include_docs_urls(title='Documentacion API'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)