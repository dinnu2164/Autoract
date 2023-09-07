from django.urls import path
from . import views

urlpatterns = [
    path('', views.image_to_kyc_data, name='image_to_kyc_data')
]
