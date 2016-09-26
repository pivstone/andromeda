"""Capella URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url

from registry import views

name_patterns = '(?P<name>[a-z0-9]+(?:[._\/-][a-z0-9]+)*)'
reference_patterns = "(?P<reference>[a-z0-9]+(:|.|-)?[a-z0-9]+)"
urlpatterns = [
    url(r'^$', views.Root.as_view()),
    url(r'^%s/tags/list$' % name_patterns, views.Tags.as_view()),
    url(r'^%s/manifests/%s$' % (name_patterns, reference_patterns), views.Manifests.as_view()),
    url(r'^%s/blobs/(?P<digest>sha256:[a-z0-9]{64})$' % name_patterns, views.Blobs.as_view()),
    url(r'^%s/blobs/uploads/$' % name_patterns, views.BlobsUploadsInit.as_view()),
    url(r'^%s/blobs/uploads/(?P<uuid>[a-z0-9]+(?:[._-][a-z0-9]+)*)$' % name_patterns, views.BlobsUploads.as_view()),
    url(r'^_catalog', views.Catalog.as_view()),
]
