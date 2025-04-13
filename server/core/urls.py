"""
URL configuration for orchard project.

The `urlpatterns` list routes URLs to views. For more information please see:
https://docs.djangoproject.com/en/5.1/topics/http/urls/
"""

from django.urls import path

from . import views

urlpatterns = [path("", views.home)]
