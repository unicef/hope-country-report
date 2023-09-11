from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.urls import path

from .views import index

urlpatterns = [
    path(r"", index, name="index"),
]
