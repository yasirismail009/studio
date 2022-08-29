from rest_framework.fields import DateTimeField, JSONField
from rest_framework.serializers import (ChoiceField, BooleanField, ModelSerializer, DateField, ValidationError,
                                        SerializerMethodField, ImageField, CharField, EmailField, IntegerField,
                                        FloatField )

from .models import SlidesData, UploadedFiles, CustomTemplate, Mp4Files
from common.enum import get_uploaded_file_status, get_mp4_file_status


class GetSlidesDataSerializer(ModelSerializer):

    class Meta:
        model = SlidesData
        fields = "__all__"


class UploadFileSerializer(ModelSerializer):

    file_name = CharField(max_length=250)

    class Meta:
        model = UploadedFiles
        fields = "__all__"


class GetUploadedFilesSerializer(ModelSerializer):
    status = SerializerMethodField('get_status', required=False)

    def get_status(self, obj):
        return get_uploaded_file_status(status=obj.status)

    class Meta:
        model = UploadedFiles
        fields = "__all__"


class GetMp4FilesSerializer(ModelSerializer):
    status = SerializerMethodField('get_status', required=False)

    def get_status(self, obj):
        return get_mp4_file_status(status=obj.status)

    class Meta:
        model = Mp4Files
        fields = "__all__"


class CustomTemplateSerializer(ModelSerializer):

    template_name = CharField(max_length=250)
    template_type = CharField(max_length=100)
    design = JSONField(default=dict)

    class Meta:
        model = CustomTemplate
        fields = "__all__"


class GetCustomTemplateSerializer(ModelSerializer):
    status = SerializerMethodField('get_status', required=False)

    def get_status(self, obj):
        return get_uploaded_file_status(status=obj.status)

    class Meta:
        model = CustomTemplate
        fields = "__all__"
