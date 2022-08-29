# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import base64
import json
import os
import random
import string

import imgkit
import requests
from PIL import Image
from django import template
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.files.temp import NamedTemporaryFile
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.safestring import SafeString
from moviepy import editor

from apps.home.models import SlidesData, UploadedFiles, CustomTemplate, Mp4Files
from apps.home.serliazers import GetSlidesDataSerializer, UploadFileSerializer, GetUploadedFilesSerializer, \
    CustomTemplateSerializer, GetMp4FilesSerializer, GetCustomTemplateSerializer
# from .tasks import process_csv_in_background, process_full_template_csv_in_background, generate_mp4_zip, process_csv_sorted
from .tasks import generate_mp4_zip, process_csv_sorted
import pandas as pd


def convert_to_base64(item):
    # for temp_student in data.get("slidesView"):
    res = requests.get(item)
    uri = ("data:" +
           res.headers['Content-Type'] + ";" +
           "base64," + str(base64.b64encode(res.content).decode("utf-8")))
    return uri


@login_required(login_url="/login/")
def premier_slides(request):
    file_name_filter = request.GET.get("file_name_filter", None)
    sorting_filter = request.GET.get("sorting_filter", None)
    render_page = request.GET.get("render_page", None)
    template_name = request.GET.get("template_name", None)
    filters_dict = {}
    # if file_name_filter:
    #     file_name_filter = request.GET.get("file_name_filter")
    if file_name_filter and file_name_filter != "default":
        filters_dict["file_name_filter"] = file_name_filter
        # sorting_filter = request.GET.get("sorting_filter", None)
        if sorting_filter and sorting_filter != "default":
            filters_dict["sorting_filter"] = sorting_filter
            if sorting_filter == "aToZ":
                data = SlidesData.objects.filter(data_source__file_name=file_name_filter,
                                                 data_source__is_duplicated=False).order_by("name")
            else:
                data = SlidesData.objects.filter(data_source__file_name=file_name_filter,
                                                 data_source__is_duplicated=False).order_by("-name")
        else:
            data = SlidesData.objects.filter(data_source__file_name=file_name_filter, data_source__is_duplicated=False)
        serialized_data = GetSlidesDataSerializer(data, many=True)

        data = {
            "slidesView": serialized_data.data
        }
    else:
        data = {
            "slidesView": []
        }

    custom_design = {
        "footer_right": "#173371"
    }

    if request.method == "POST":

        download_type = request.POST.get("download_type", "").lower()
        render_template = request.POST.get("render_page", "").lower()
        print(render_template)
        if "single" in download_type:
            print("DOWNLOAD SINGLE FILE")
            print(request.POST)

            student_id = int(request.POST.get("student_id"))
            template_id = request.POST.get("template_id")
            print("STUDENT_ID: ", student_id)
            print("template_id: ", template_id)

            data = SlidesData.objects.get(pk=student_id)
            serialized_data = GetSlidesDataSerializer(data)
            entity = CustomTemplate.objects.get(pk=template_id)
            serialized_template_entity = GetCustomTemplateSerializer(entity).data
            custom_dict = {}
            student = serialized_data.data
            student_name = student.get("name")
            student["download"] = "yes"
            custom_dict["slidesView"] = [student]
            temp_data = {'slidesView': SafeString(json.loads(json.dumps([student]))),
                         'custom_css': json.loads(json.dumps(serialized_template_entity))
                         }
            if render_template == "full_template":
                file_name_filter = request.POST.get("file_name_filter", None)
                query_set = UploadedFiles.objects.filter(file_name=file_name_filter, is_duplicated=False)
                if query_set:
                    background_image = query_set.last().background_image
                    temp_data["background_image"] = background_image
                content = render_to_string('home/customize_full_template_skeleton.html', temp_data)

            else:
                content = render_to_string('home/slide_only_template_for_download.html', temp_data)
            new_file = NamedTemporaryFile(prefix=student.get("name", "") + "_", suffix='.html')
            with open(new_file.name, 'w+') as static_file:
                static_file.write(content)

            # Kit options in case PDF is to be generated
            # kit_options = {
            #     "--enable-local-file-access": None,
            #     "--enable-javascript": None,
            #     "--debug-javascript": None,
            # }

            kit_options = {
                "--disable-smart-width": None,
                "--quality": 100,
                'width': 1920,
                'height': 1080,
                "--enable-local-file-access": None
                # "--page-size": "A4"
                # 'crop-w': '3',
            }
            mp4_temp_file = NamedTemporaryFile(prefix=student_name + "_", suffix='.mp4')
            image_temp_file = NamedTemporaryFile(prefix=student_name + "_", suffix='.png')
            with open("test.html", "a") as test_html:
                test_html.write(content)
            imgkit.from_string(content, image_temp_file.name, options=kit_options)
            # is_windows = sys.platform.startswith('win')

            # TODO: Uncomment this to download MP4
            audio = editor.AudioFileClip('testing.mp3')
            video = editor.ImageClip(image_temp_file.name)
            video.fps = 25
            video.duration = audio.duration
            final_video = video.set_audio(audio)
            print(mp4_temp_file.name)
            final_video.write_videofile(mp4_temp_file.name, fps=1)

            # if is_windows:
            #     ffmpeg_path = 'C:/ffmpeg/bin/ffmpeg.exe'
            #     os.system(
            #         f'cmd /c {ffmpeg_path} -loop 1 -i "{image_temp_file.name}" -i testing.mp3 -c:v libx264 -tune '
            #         f'stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -t 00:00:06 "{mp4_temp_file.name}" -y')

            f = open(mp4_temp_file.name, 'rb')

            response = HttpResponse(mp4_temp_file.read(), content_type="video/mp4v")
            response['Content-Length'] = os.path.getsize(mp4_temp_file.name)
            response['Content-Disposition'] = \
                "attachment; filename=\"%s\"; filename*=utf-8''%s" % \
                (mp4_temp_file.name, student_name + ".mp4")
            # f.close()
            return response

            # To download IMAGE
            # response = HttpResponse(image_temp_file.read(), content_type="image/png")
            # response['Content-Length'] = os.path.getsize(image_temp_file.name)
            # response['Content-Disposition'] = \
            #     "attachment; filename=\"%s\"; filename*=utf-8''%s" % \
            #     (image_temp_file.name, student_name + ".png")
            # # f.close()
            # return response

        if "all" in download_type:
            print("DOWNLOAD ALL FILES")
            template_id = request.POST.get("template_id")
            file_name_filter = request.POST.get("file_name_filter", None)

            splitted_name = file_name_filter.split(".")[0]
            random_values = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            mp4_zip_name = splitted_name + random_values
            entity = SlidesData.objects.filter(data_source__file_name=file_name_filter)
            serialized_entity = GetSlidesDataSerializer(entity, many=True)
            json_converted_data = json.loads(json.dumps(serialized_entity.data))
            Mp4Files.objects.filter(file_name=mp4_zip_name + ".zip", is_duplicated=False).update(
                is_duplicated=True)
            Mp4Files(file_name=mp4_zip_name + ".zip").save()
            generate_mp4_zip.delay(str(mp4_zip_name), json_converted_data, template_id,
                                   str(render_template), str(file_name_filter))
            return HttpResponseRedirect("mp4_listing")

    uploaded_files_list = list(SlidesData.objects.values_list('data_source__file_name', flat=True).distinct())
    custom_template_list = list(CustomTemplate.objects.filter(template_type=render_page.strip()).
                                values_list('template_name', flat=True))
    # print(custom_template_list)
    if file_name_filter:
        query_params = file_name_filter
    else:
        query_params = ""

    # print(json.loads(json.dumps(data['slidesView'])))

    context_details = {
        'slidesView': json.loads(json.dumps(data['slidesView'])),
        # 'slidesView': data['slidesView'],
        'uploaded_csv_files': json.loads(json.dumps(uploaded_files_list)),
        'query_params': json.loads(json.dumps(query_params)),
        "filters": filters_dict,
        "custom_template_list": custom_template_list,
    }
    if template_name and template_name != "default":
        custom_template = CustomTemplate.objects.get(template_type=render_page.strip(), template_name=template_name)
        custom_template_serialized = CustomTemplateSerializer(custom_template)
        # print(custom_template_serialized.data)
        context_details["custom_css"] = json.loads(json.dumps(custom_template_serialized.data))

    render_page = request.GET.get("render_page", None)
    if render_page and render_page == "full_template":
        page_to_be_rendered = "full_template"
        if file_name_filter and file_name_filter != "default":
            background_image = UploadedFiles.objects.filter(file_name=file_name_filter).last().background_image
            if background_image:
                context_details["background_image"] = background_image
    else:
        page_to_be_rendered = "lower_third"

    context_details["render_page"] = page_to_be_rendered

    return render(request, "home/premier_slides.html", context_details)


# def upload_CSV(request):
#     if request.method == "POST":
#         print(request.POST)
#         try:
#             request_body = request.POST
#             if request_body.get("form_type").strip() == "lower_third":
#                 try:
#                     csv_file = request.FILES['myfile']
#                 except Exception as file_exc:
#                     messages.error(request, "Invalid Data Source !")
#                     return render(request, "home/uploads_csv.html")
#
#                 default_image = request.FILES['default_image']
#                 if csv_file:
#
#                     SlidesData.objects.filter(data_source__file_name=str(csv_file).strip()).delete()
#                     UploadedFiles.objects.filter(file_name=str(csv_file).strip()).update(is_duplicated=True)
#
#                     data_obj = {
#                         "file_name": str(csv_file).strip()
#                     }
#
#                     entity_serialized = UploadFileSerializer(data=data_obj)
#                     if entity_serialized.is_valid():
#                         entity_serialized.save()
#                         path = default_storage.save(str(csv_file), ContentFile(csv_file.read()))
#                         tmp_file = os.path.join(settings.MEDIA_ROOT, path)
#
#                         img_path = default_storage.save(str(default_image), ContentFile(default_image.read()))
#                         img_tmp_file = os.path.join(settings.MEDIA_ROOT, img_path)
#
#                         csv_name = str(csv_file)
#                         csv_path = str(tmp_file)
#                         default_image_name = str(default_image)
#                         default_image_path = str(img_tmp_file)
#
#                         x = process_csv_in_background.delay(request_body, csv_name, csv_path, default_image_name,
#                                                             default_image_path)
#                         print(x.task_id)
#                         messages.info(request, 'Data Processing Started.')
#                         return render(request, "home/uploads_csv.html")
#                     else:
#                         messages.error(request, entity_serialized.errors)
#                         return render(request, "home/uploads_csv.html")
#             # In case of FULL TEMPLATE DESIGN
#             elif request_body.get("form_type").strip() == "full_template":
#                 print("Full template csv uploaded")
#                 try:
#                     csv_file = request.FILES['csv_file']
#                 except Exception as file_exc:
#                     messages.error(request, "Invalid Data Source !")
#                     return render(request, "home/uploads_csv.html")
#
#                 default_image = request.FILES['default_image']
#                 # background_image = request.FILES['background_image']
#                 if csv_file:
#                     SlidesData.objects.filter(data_source__file_name=str(csv_file).strip()).delete()
#                     UploadedFiles.objects.filter(file_name=str(csv_file).strip()).update(is_duplicated=True)
#                     # bg_img_path = default_storage.save(str(background_image), ContentFile(background_image.read()))
#                     # img_tmp_file = os.path.join(settings.MEDIA_ROOT, bg_img_path)
#                     # bg_path = str(img_tmp_file)
#                     # bg_img = Image.open(bg_path)
#                     data_obj = {}
#                     # print("MIME : {0} ".format(bg_img.get_format_mimetype()))
#                     # with open(bg_path, "rb") as temp_img:
#                     #     data_obj["background_image"] = "data:" + bg_img.get_format_mimetype() + ";" + "base64," + \
#                     #                                    str(base64.b64encode(temp_img.read()).decode("utf-8"))
#                     # bg_img.close()
#
#                     data_obj["file_name"] = str(csv_file).strip()
#
#                     entity_serialized = UploadFileSerializer(data=data_obj)
#                     if entity_serialized.is_valid():
#                         entity_serialized.save()
#
#                         path = default_storage.save(str(csv_file), ContentFile(csv_file.read()))
#                         tmp_file = os.path.join(settings.MEDIA_ROOT, path)
#
#                         img_path = default_storage.save(str(default_image), ContentFile(default_image.read()))
#                         img_tmp_file = os.path.join(settings.MEDIA_ROOT, img_path)
#
#                         csv_name = str(csv_file)
#                         csv_path = str(tmp_file)
#                         default_image_name = str(default_image)
#                         default_image_path = str(img_tmp_file)
#
#                         x = process_full_template_csv_in_background.delay(request_body, csv_name, csv_path,
#                                                                           default_image_name,
#                                                                           default_image_path, "")
#                         print(x.task_id)
#                         messages.info(request, 'Data Processing Started.')
#                         return render(request, "home/uploads_csv.html")
#                     else:
#                         messages.error(request, entity_serialized.errors)
#                         return render(request, "home/uploads_csv.html")
#         except Exception as ex:
#             messages.error(request, str(ex))
#             return render(request, "home/uploads_csv.html")
#
#     return render(request, "home/uploads_csv.html")


def upload_CSV_stepper(request):
    context = {"step": 1}
    if request.method == "POST":
        try:
            request_body = request.POST
            request_step = request_body.get("step", 0)
            request_step = int(request_step)
            print("STEP: ", request_step)
            if request_step == 1:
                print("POST CALL RECEIVED FROM STEP 1")
                context["step"] = 2
                csv_file = request.FILES['csv_file']
                print(request.POST)
                if csv_file:
                    try:
                        file_type = str(csv_file).strip().split(".")[-1]
                        if not file_type.lower() == "csv":
                            context["step"] = 4
                            messages.error(request, "ERROR: Not a valid CSV file")
                            return render(request, "home/upload_CSV_stepper.html", context)
                    except Exception as file_type_exception:
                        print(file_type_exception)
                        context["step"] = 4
                        messages.error(request, "ERROR: " + str(file_type_exception))
                        return render(request, "home/upload_CSV_stepper.html", context)

                    SlidesData.objects.filter(data_source__file_name=str(csv_file).strip()).delete()
                    UploadedFiles.objects.filter(file_name=str(csv_file).strip()).update(is_duplicated=True)
                    path = default_storage.save(str(csv_file), ContentFile(csv_file.read()))
                    tmp_file = os.path.join(settings.MEDIA_ROOT, path)
                    # csv_name = str(csv_file)
                    csv_path = str(tmp_file)
                    # Reading csv in pd dataframe
                    df = pd.read_csv(csv_path)
                    # column_headers = list(df.columns)
                    # csv_data = df.to_json()
                    context["temp_file_path"] = path
                    context["original_file_name"] = str(csv_file)
                    context["df"] = df
                    # messages.info(request, 'Data Processing Started.')
                    return render(request, "home/upload_CSV_stepper.html", context)
                return render(request, "home/upload_CSV_stepper.html", context)

            elif request_step == 2:
                print("POST CALL RECEIVED FROM STEP 2")
                request_body = request.POST
                print(request_body)
                is_sort_modal = request_body.get("modal_sort")
                is_save_sorting = request_body.get("save_sorting")

                csv_name = request_body.get("temp_file_path")
                original_file_name = request_body.get("original_file_name")
                # print(csv_name)
                csv_path = os.path.join(settings.MEDIA_ROOT, csv_name)
                if is_sort_modal:
                    df = pd.read_csv(csv_path)
                    substring = "Unnamed"
                    extra_columns = [substring_to_drop for substring_to_drop in list(df.columns) if
                                     substring in substring_to_drop]
                    # print(extra_columns)
                    if extra_columns:
                        df = df.drop(extra_columns, axis=1)

                    sort_columns = []
                    sort_ascending = []
                    for key in request.POST.keys():
                        if "sorting_" in key.lower():
                            sort_columns.append(request_body.get(key))
                        elif "order_" in key.lower():
                            if "ascending" in request_body.get(key).lower():
                                sort_ascending.append(True)
                            else:
                                sort_ascending.append(False)
                    original_csv_name = request_body.get("temp_file_path")
                    spliited_name = original_csv_name.split(".")[0]
                    sorted_df = df.sort_values(by=sort_columns, ascending=sort_ascending)
                    substring = "Unnamed"
                    extra_columns = [substring_to_drop for substring_to_drop in list(df.columns) if
                                     substring in substring_to_drop]
                    # print(extra_columns)
                    if extra_columns:
                        sorted_df = sorted_df.drop(extra_columns, axis=1)

                    substring = ""
                    if substring in list(df.columns):
                        sorted_df = sorted_df.drop([""], axis=1)

                    context["df"] = sorted_df
                    context["sorting_columns"] = sort_columns
                    context["sorting_ascending"] = sort_ascending
                    random_string = ''.join((random.choice(string.ascii_lowercase)) for x in range(6))
                    sorted_csv_file_name = f'media/{spliited_name}_{random_string}.csv'
                    sorted_df.to_csv(sorted_csv_file_name, index=None)
                    csv_path = os.path.join(settings.MEDIA_ROOT, original_csv_name)

                    context["temp_file_path"] = f'{spliited_name}_{random_string}.csv'
                    context["temp_file_name"] = f'{spliited_name}_{random_string}.csv'
                    context["original_file_name"] = original_file_name
                    context["step"] = 2

                    # print(sorted_df.columns)
                    os.remove(csv_path)
                    return render(request, "home/upload_CSV_stepper.html", context)
                # context["df"] = df
                if is_save_sorting:
                    df = pd.read_csv(csv_path)
                    context["step"] = 3
                    context["columns"] = list(df.columns)

                    context["temp_file_path"] = csv_path
                    context["temp_file_name"] = csv_name
                    context["original_file_name"] = original_file_name

                    print("step 3 rendered on screen")
                    return render(request, "home/upload_CSV_stepper.html", context)

            elif request_step == 3:
                print("POST CALL RECEIVED FROM STEP 3")
                print(request.POST)
                request_body = request.POST
                csv_name = request_body.get("temp_file_name")
                csv_path = request_body.get("temp_file_path")
                original_file_name = request_body.get("original_file_name")
                # temp_df = pd.read_csv(csv_path)
                # print(temp_df.iloc[[1]])
                # df_columns = list(df.columns)

                # print("COLUMNS: ", df_columns)
                SlidesData.objects.filter(data_source__file_name=str(original_file_name).strip()).delete()
                UploadedFiles.objects.filter(file_name=str(original_file_name).strip()).update(is_duplicated=True)
                data_obj = {
                    "file_name": str(original_file_name).strip()
                }
                serialized_entity = UploadFileSerializer(data=data_obj)
                if serialized_entity.is_valid():
                    serialized_entity.save()
                    df = pd.read_csv(csv_path)
                    substring = "Unnamed"
                    extra_columns = [substring_to_drop for substring_to_drop in list(df.columns) if
                                     substring in substring_to_drop]
                    # print(extra_columns)
                    if extra_columns:
                        df = df.drop(extra_columns, axis=1)
                    if "" in list(df.columns):
                        df = df.drop(extra_columns, axis=1)
                    # print(df.iloc[[1]])

                    df_columns = list(df.columns)
                    # print("COLUMNS AFTER DROPPING: ", df_columns)
                    task = process_csv_sorted.delay(request_body, str(original_file_name).strip(), csv_path, df_columns)
                    print(task.id)
                    csv_path = request.POST.get("temp_file_path")
                    print("csv path in last step: ", csv_path)
                    csv_path = os.path.join(settings.MEDIA_ROOT, csv_path)
                    # df = pd.read_csv(csv_path)
                    # column_headers = list(df.columns)
                    # csv_data = df.to_json()
                    context["temp_file_path"] = csv_path
                    # context["df"] = df
                    context["step"] = 4
                    messages.info(request, "CSV processing started")
                    return render(request, "home/upload_CSV_stepper.html", context)
                else:
                    context["step"] = 4
                    messages.error(request, "ERROR: " + str(serialized_entity.errors))
                    return render(request, "home/upload_CSV_stepper.html", context)
            else:
                print("invalid step ")

        except Exception as ex:
            print(ex)
            messages.error(request, str(ex))
            return render(request, "home/upload_CSV_stepper.html")

    return render(request, "home/upload_CSV_stepper.html", context)


@login_required(login_url="/login/")
def customize_template(request):
    if request.method == 'POST':
        request_data = request.POST
        template_name = request_data.get("template_name", None)
        template_type = request_data.get("template_type", None)
        if template_name and template_type:
            entity = CustomTemplate.objects.filter(template_name=template_name.strip(),
                                                   template_type=template_type.strip()).first()
            if entity:
                messages.error(request, 'Template Name Already Exists !')
                print('Template Name Already Exists !')
            else:

                # custom_template = CustomTemplate.objects.get(template_type=render_page.strip(),
                #                                              template_name=template_name)
                # custom_template_serialized = CustomTemplateSerializer(custom_template)
                # print(custom_template_serialized.data)
                # context_details["custom_css"] = json.loads(json.dumps(custom_template_serialized.data))
                #

                data = {"template_name": template_name,
                        "template_type": template_type,
                        "image": "",
                        "design": request_data}
                serialized_data = CustomTemplateSerializer(data=data)
                if serialized_data.is_valid():
                    entity_obj = serialized_data.save()
                    data_to_send = {
                        "custom_css": {
                            "design": serialized_data.data.get("design")
                        }
                    }
                    content = render_to_string('home/customize_full_template_skeleton.html', data_to_send)

                    kit_options = {
                        "--disable-smart-width": None,
                        "--quality": 100,
                        'width': 1920,
                        'height': 1080,
                        "--enable-local-file-access": None
                        # "--page-size": "A4"
                        # 'crop-w': '3',
                    }
                    image_temp_file = NamedTemporaryFile(prefix=serialized_data.data.get("template_name") + "_",
                                                         suffix='.png')

                    imgkit.from_string(content, image_temp_file.name, options=kit_options)
                    print(image_temp_file.name)
                    with open(image_temp_file.name, "rb") as img_file:
                        b64_string = base64.b64encode(img_file.read()).decode("utf-8")
                        # print(b64_string)
                        entity_obj.image = "data:image/png;" + "base64," + str(b64_string)
                        entity_obj.save()
                    messages.info(request, 'Template Saved.')
                else:
                    messages.error(request, 'Error saving template.')
                    print(serialized_data.errors)
        else:
            messages.error(request, 'Error saving template.')
            print("template Name: ", template_name)
            print("template Type: ", template_type)

    return render(request, "home/customize_full_template.html")


@login_required(login_url="/login/")
def csv_listing(request):
    if request.method == 'POST':
        pass
    entity = UploadedFiles.objects.all().order_by("-uploaded_date")
    entity_serialized = GetUploadedFilesSerializer(entity, many=True)
    return render(request, "home/csv_listing.html",
                  {"uploaded_files_data": json.loads(json.dumps(entity_serialized.data))})


@login_required(login_url="/login/")
def mp4_listing(request):
    if request.method == 'POST':
        pass
    entity = Mp4Files.objects.all().order_by("-requested_date")
    entity_serialized = GetMp4FilesSerializer(entity, many=True)
    print(entity_serialized.data)
    context = {
        "mp4_files_data": json.loads(json.dumps(entity_serialized.data)),
        "segment": "mp4_listing"
    }
    return render(request, "home/mp4_listing.html", context)


@login_required(login_url="/login/")
def template_listing(request):
    if request.method == 'POST':
        pass
    else:
        # template_id = request.GET.get("id")
        # if template_id:
        #     template_id = int(template_id)
        #     custom_template = CustomTemplate.objects.get(pk=template_id)
        #     custom_template_serialized = CustomTemplateSerializer(custom_template)
        #     print(custom_template_serialized.data)
        #     context_details = {"custom_css": json.loads(json.dumps(custom_template_serialized.data))}
        #     return render(request, "home/template_listing.html",
        #                   context_details)

        custom_template = CustomTemplate.objects.all()
        custom_template_serialized = CustomTemplateSerializer(custom_template, many=True)
        # print(custom_template_serialized.data)
        context_details = {"custom_css_list": json.loads(json.dumps(custom_template_serialized.data))}
        # print(custom_template_serialized[0])

        return render(request, "home/template_listing.html",
                      context_details)


@login_required(login_url="/login/")
def fullscreen_slide_view(request):
    if request.method == 'POST':
        pass
    else:
        # template_id = request.GET.get("id")
        # if template_id:
        #     template_id = int(template_id)
        #     custom_template = CustomTemplate.objects.get(pk=template_id)
        #     custom_template_serialized = CustomTemplateSerializer(custom_template)
        #     print(custom_template_serialized.data)
        #     context_details = {"custom_css": json.loads(json.dumps(custom_template_serialized.data))}
        #     return render(request, "home/template_listing.html",
        #                   context_details)

        query_params = request.GET
        template_type = query_params.get("template_type")
        template_id = query_params.get("template_id")
        custom_template = CustomTemplate.objects.get(pk=template_id, template_type=template_type)
        custom_template_serialized = CustomTemplateSerializer(custom_template)
        # print(custom_template_serialized.data)
        context_details = {"custom_css": json.loads(json.dumps(custom_template_serialized.data))}
        # print(custom_template_serialized[0])
        data = custom_template_serialized.data
        del data["image"]
        print(data.keys())
        return render(request, "home/fullscreen_slide_view.html",
                      context_details)


@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    # html_template = loader.get_template('home/index.html')
    html_template = loader.get_template('home/select_slides.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template
        try:
            html_template = loader.get_template('home/' + load_template)
            return HttpResponse(html_template.render(context, request))
        except Exception as ex:
            print(ex)
            html_template = loader.get_template('home/' + load_template)
            return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))
