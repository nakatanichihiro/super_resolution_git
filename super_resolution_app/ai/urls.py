from django.contrib import admin
from django.urls import include, path
from django.urls import path

from . import views
from super_resolution_app.users.views import (
    user_redirect_view,
    user_update_view,
    user_detail_view,
)


app_name = "ai"
urlpatterns = [
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("<str:username>/", view=user_detail_view, name="detail"),
    path('index', views.index, name='index'),
    path('resolution', views.resolution, name='resolution'),
    path('resolution_example', views.resolution_example, name="resolution_example"),
    path('doResolution', views.doResolution, name='doResolution'),
    path('top', views.top, name='top'),

    # ファイルアップロード用
    # path('monitor/upload/', views.upload, name='upload'),
    # path('monitor/upload_complete/', views.upload_complete, name='upload_complete'),

]
