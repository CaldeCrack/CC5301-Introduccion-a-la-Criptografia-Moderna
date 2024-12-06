from django.contrib import admin
from django.urls import path
from app import views


urlpatterns = [
    path('admin/', admin.site.urls),
	path("", views.index, name="index"),
	path('chat/<int:usuario_id>/', views.chat, name='chat'),
]
