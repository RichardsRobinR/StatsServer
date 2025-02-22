from django.urls import include, path

from metrics import views

urlpatterns = [
    path('', views.get_metrics, name='get_metrics'),
]
