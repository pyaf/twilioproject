from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.views import logout
from .views import IndexView, DashboardView, LoginView

urlpatterns = [
    url(r'^$', IndexView.as_view(), name="index"),
    url(r'^login/$', LoginView.as_view(), name="login_url"),
    url(r'^dashboard/$', DashboardView.as_view(), name="dashboard"),
    url(r'^logout/$', logout, {'next_page': '/'})

]
