# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('premier_slides', views.premier_slides, name='premiere_slides_view'),
    path('upload_csv', views.upload_CSV_stepper, name='upload_csv'),
    path('customize_full_template', views.customize_template, name='customize_template'),
    path('csv_listing', views.csv_listing, name='csv_listing'),
    path('mp4_listing', views.mp4_listing, name='mp4_listing'),
    path('template_listing', views.template_listing, name='template_listing'),
    path('fullscreen_slide_view', views.fullscreen_slide_view, name='fullscreen_slide_view'),
    path('upload_CSV_stepper', views.upload_CSV_stepper, name='upload_CSV_stepper'),

    # Matches any html file
    re_path(r'^.*\.html', views.pages, name='pages'),

]
