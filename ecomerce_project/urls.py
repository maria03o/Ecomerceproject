
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import  include, path
#from allauth.account.urls import 
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('catalog.urls')),
    path('accounts/', include('allauth.urls')),
   
]


if settings.DEBUG: 
 urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
 urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)  # Use STATIC_ROOT


