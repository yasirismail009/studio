# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class UploadedFiles(models.Model):

    file_name = models.CharField(max_length=250)
    uploaded_date = models.DateTimeField(auto_now_add=True)
    background_image = models.TextField(null=True, blank=True)
    status = models.IntegerField(default=1)
    is_duplicated = models.BooleanField(default=False)

    class Meta:
        db_table = "uploaded_files"


class Mp4Files(models.Model):
    file_name = models.CharField(max_length=250)
    requested_date = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(default=1)
    is_duplicated = models.BooleanField(default=False)

    class Meta:
        db_table = "mp4_files"


class SlidesData(models.Model):
    name = models.CharField(max_length=100, default="")
    major = models.CharField(max_length=250, default="")
    school = models.CharField(max_length=250, default="")
    honor = models.CharField(max_length=250, default="")
    quote = models.CharField(max_length=250, default="")
    image = models.TextField(default="")
    audio = models.CharField(max_length=250, default="")
    data_source = models.ForeignKey(UploadedFiles, blank=True, related_name="%(app_label)s_%(class)s_data_source",
                                    null=True, on_delete=models.PROTECT)
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(default=2)

    class Meta:
        db_table = "slides_data"


class CustomTemplate(models.Model):
    template_name = models.CharField(max_length=250)
    template_type = models.CharField(max_length=100)
    design = models.JSONField(max_length=250)
    status = models.IntegerField(default=2)
    image = models.TextField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "custom_templates"
