from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings
from django.urls import path
from app import views


urlpatterns = [
    path('admin/', admin.site.urls),
	path("", views.home, name='home'),
	path('register/', views.register, name='register'),
    path('login/', views.login2, name='login2'),
    path('logout/', views.logout2, name='logout2'),
	path('home/', views.home, name='home'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
