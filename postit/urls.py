from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('about/', include('about.urls', namespace='about')),
    path('', include('posts.urls')),
]
