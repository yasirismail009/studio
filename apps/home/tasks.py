"""
THIS FILE CONTAINS BACKGROUND TASKS THAT ARE TO BE RUN TO QUEUE THE PRODUCERS
"""
from __future__ import absolute_import, unicode_literals
import base64
import json
import os
import re
import sys
import zipfile
from tempfile import NamedTemporaryFile

import imgkit
import requests
from celery import shared_task
import logging
import csv
import io
from PIL import Image
from django.template.loader import render_to_string
from django.utils.safestring import SafeString
from moviepy import editor
from apps.home.models import SlidesData, UploadedFiles, CustomTemplate, Mp4Files
from apps.home.serliazers import GetCustomTemplateSerializer

logger = logging.getLogger(__name__)


def convert_to_base64(item):
    # for temp_student in data.get("slidesView"):
    try:

        res = requests.get(item)
        uri = ("data:" +
               res.headers['Content-Type'] + ";" +
               "base64," + str(base64.b64encode(res.content).decode("utf-8")))
        return uri
    except Exception as image_exc:
        print(image_exc)
        return None

#
# @shared_task(name="process_csv_in_background")
# def process_csv_in_background(request_body, csv_name, csv_path, default_image_name, default_image_path):
#     """
#     This method will process the uploaded CSV in background.
#     """
#     data_source = UploadedFiles.objects.get(file_name=csv_name, is_duplicated=False)
#     try:
#         logger.info('====================Fetching Values====================')
#         name_column = request_body.get("name_column", None)
#         major_column = request_body.get("major_column", None)
#         school_column = request_body.get("school_column", None)
#         honor_column = request_body.get("honor_column", None)
#         image_column = request_body.get("image_column", None)
#         # print(str(default_image))
#         with open(csv_path, "r") as csv_file:
#             logger.info('====================CSV Processing Started====================')
#
#             # Delete previous uploaded data from same file to avoid duplication
#             # Decode and process the data
#             decoded_file = csv_file.read()
#             io_string = io.StringIO(decoded_file)
#             count = 0
#             # data_source = UploadedFiles.objects.get(file_name=csv_name, is_duplicated=False)
#             data_source_id = data_source.id
#
#             for line in csv.reader(io_string, delimiter=',', quotechar='|'):
#                 if count == 0:
#                     count += 1
#                     continue
#                 else:
#                     temp_obj = {"id": count}
#                     if name_column:
#                         temp_obj["name"] = line[int(name_column)]
#                     else:
#                         temp_obj["name"] = ""
#                     if major_column:
#                         temp_obj["major"] = line[int(major_column)]
#                     else:
#                         temp_obj["major"] = ""
#                     if school_column:
#                         temp_obj["school"] = line[int(school_column)]
#                     else:
#                         temp_obj["school"] = ""
#                     if honor_column:
#                         temp_obj["honor"] = line[int(honor_column)]
#                     else:
#                         temp_obj["honor"] = ""
#                     if image_column and str(line[int(image_column)]).strip() != "":
#                         temp_obj["image"] = convert_to_base64(str(line[int(image_column)]))
#
#                     else:
#                         pass
#                         im1 = Image.open(default_image_path)
#                         logger.info("MIME : {0} ".format(im1.get_format_mimetype()))
#                         with open(default_image_path, "rb") as temp_img:
#                             temp_obj["image"] = "data:" + im1.get_format_mimetype() + ";" + "base64," + \
#                                                 str(base64.b64encode(temp_img.read()).decode("utf-8"))
#                         im1.close()
#                     temp_obj["Audio"] = ""
#                     logger.info('Count:  {0} '.format(str(count)))
#                     SlidesData(
#                         name=temp_obj["name"],
#                         major=temp_obj["major"],
#                         school=temp_obj["school"],
#                         honor=temp_obj["honor"],
#                         image=temp_obj["image"],
#                         audio=temp_obj["Audio"],
#                         data_source_id=data_source_id
#                     ).save()
#                     count += 1
#
#         data_source.status = 2
#         data_source.save()
#
#         logger.info('====================CSV Processing Finished====================')
#         logger.info('Removing File:  1. {0} \n 2. {1} '.format(str(csv_path), str(default_image_path)))
#         os.remove(csv_path)
#         os.remove(default_image_path)
#         logger.info('====================Garbage Cleaning Done====================')
#         return True
#     except Exception as exc:
#         data_source.status = 3
#         data_source.save()
#         print(exc)
#         return False
#
#
# @shared_task(name="process_full_template_csv_in_background")
# def process_full_template_csv_in_background(request_body, csv_name, csv_path, default_image_name, default_image_path,
#                                             bg_path):
#     """
#     This method will process the uploaded Full template CSV in background.
#     """
#     data_source = UploadedFiles.objects.get(file_name=csv_name, is_duplicated=False)
#     try:
#         logger.info('====================Fetching Values====================')
#         logger.info(request_body)
#         name_column = request_body.get("name_column", None)
#         major_column = request_body.get("major_column", None)
#         school_column = request_body.get("school_column", None)
#         honor_column = request_body.get("honor_column", None)
#         image_column = request_body.get("image_column", None)
#         quote_column = request_body.get("quote_column", None)
#         # print(str(default_image))
#         with open(csv_path, "r") as csv_file:
#             logger.info('====================CSV Processing Started====================')
#
#             # Delete previous uploaded data from same file to avoid duplication
#             # Decode and process the data
#             decoded_file = csv_file.read()
#             io_string = io.StringIO(decoded_file)
#             count = 0
#             # data_source = UploadedFiles.objects.get(file_name=csv_name, is_duplicated=False)
#             data_source_id = data_source.id
#
#             for line in csv.reader(io_string, delimiter=',', quotechar='"'):
#                 if count == 0:
#                     count += 1
#                     continue
#                 else:
#                     temp_obj = {"id": count}
#                     if name_column:
#                         temp_obj["name"] = line[int(name_column)]
#                     else:
#                         temp_obj["name"] = ""
#                     if major_column:
#                         temp_obj["major"] = line[int(major_column)]
#                     else:
#                         temp_obj["major"] = ""
#                     if school_column:
#                         temp_obj["school"] = line[int(school_column)]
#                     else:
#                         temp_obj["school"] = ""
#                     if honor_column:
#                         temp_obj["honor"] = line[int(honor_column)]
#                     else:
#                         temp_obj["honor"] = ""
#                     if quote_column:
#                         temp_obj["quote"] = line[int(quote_column)]
#                     else:
#                         temp_obj["quote"] = ""
#
#                     if image_column and str(line[int(image_column)]).strip() != "":
#                         temp_obj["image"] = convert_to_base64(str(line[int(image_column)]))
#
#                         # print("converted image data : ", temp_obj.get("image"))
#                     else:
#                         pass
#                         im1 = Image.open(default_image_path)
#                         #
#                         # default_file_image_name = "media/" + str(default_image)
#                         # im1.save(default_file_image_name)
#                         logger.info("MIME : {0} ".format(im1.get_format_mimetype()))
#                         with open(default_image_path, "rb") as temp_img:
#                             temp_obj["image"] = "data:" + im1.get_format_mimetype() + ";" + "base64," + \
#                                                 str(base64.b64encode(temp_img.read()).decode("utf-8"))
#                         im1.close()
#                     temp_obj["Audio"] = ""
#                     logger.info('Count:  {0} '.format(str(count)))
#                     # logger.info(temp_obj)
#                     SlidesData(
#                         name=temp_obj["name"],
#                         major=temp_obj["major"],
#                         school=temp_obj["school"],
#                         honor=temp_obj["honor"],
#                         image=temp_obj["image"],
#                         audio=temp_obj["Audio"],
#                         quote=temp_obj["quote"],
#                         data_source_id=data_source_id
#                     ).save()
#                     count += 1
#
#         data_source.status = 2
#         data_source.save()
#
#         logger.info('====================CSV Processing Finished====================')
#         logger.info('Removing File:  1. {0} \n \n 2. {1}\n \n 3. {2} \n \n '.format(
#             str(csv_path), str(default_image_path), bg_path))
#
#         os.remove(csv_path)
#         os.remove(default_image_path)
#         # os.remove(bg_path)
#         logger.info('====================Garbage Cleaning Done====================')
#         return True
#     except Exception as exc:
#         data_source.status = 3
#         data_source.save()
#         print(exc)
#         return False


@shared_task(name="generate_mp4_zip")
def generate_mp4_zip(mp4_zip_name, json_converted_data, template_id, render_template, file_name_filter):
    """
    This method will process the uploaded Full template CSV in background.
    """
    entity = CustomTemplate.objects.get(pk=template_id)
    custom_design = GetCustomTemplateSerializer(entity).data

    with open("media/" + mp4_zip_name + ".zip", 'wb+') as zipMe:
        for student in json_converted_data:
            student_name = student.get("name", "").strip()
            # custom_dict["slidesView"] = [student]
            temp_data = {'slidesView': json.loads(json.dumps([student])),
                         'custom_css': json.loads(json.dumps(custom_design))
                         }
            mp4_temp_file = NamedTemporaryFile(prefix=student_name + "_", suffix='.mp4')
            image_temp_file = NamedTemporaryFile(prefix=student_name + "_", suffix='.png')
            mp4_converted_path = str(mp4_temp_file.name).replace(" ", "_")
            if render_template == "full_template":
                query_set = UploadedFiles.objects.filter(file_name=file_name_filter, is_duplicated=False)
                if query_set:
                    background_image = query_set.last().background_image
                    temp_data["background_image"] = background_image
                content = render_to_string('home/customize_full_template_skeleton.html', temp_data)

            else:
                content = render_to_string('home/slide_only_template_for_download.html', temp_data)

            kit_options = {
                "--disable-smart-width": None,
                "--quality": 100,
                'width': 1920,
                'height': 1080,
                "--enable-local-file-access": None,
                "--quiet": None,

            }
            pic_path = str(image_temp_file.name).replace(" ", "_")

            imgkit.from_string(content, pic_path, options=kit_options)

            audio = editor.AudioFileClip('testing.mp3')
            video = editor.ImageClip(pic_path)
            video.fps = 1
            video.duration = audio.duration
            final_video = video.set_audio(audio)

            final_video.write_videofile(mp4_converted_path, fps=1, verbose=False, logger=None)
            with zipfile.ZipFile(zipMe, 'a', zipfile.ZIP_DEFLATED) as archive:
                archive.write(str(mp4_converted_path))

    Mp4Files.objects.filter(file_name=mp4_zip_name + ".zip", is_duplicated=False).update(status=2)


@shared_task(name="process_csv_sorted")
def process_csv_sorted(request_body, csv_name, csv_path, df_columns):
    """
    This method will process the uploaded Full template CSV in background.
    """
    data_source = UploadedFiles.objects.get(file_name=csv_name, is_duplicated=False)
    try:
        print(df_columns)
        logger.info('====================Fetching Values====================')
        logger.info(request_body)
        placeholder_1 = request_body.get("placeholder_1", None)
        placeholder_2 = request_body.get("placeholder_2", None)
        placeholder_3 = request_body.get("placeholder_3", None)
        image_placeholder = request_body.get("image_placeholder", None)
        placeholder_4 = request_body.get("placeholder_4", None)
        # print("NAME PLACEHOLDER: ", placeholder_1)
        if placeholder_1:
            name_column = df_columns.index(placeholder_1)
        else:
            name_column = None
        if placeholder_2:
            major_column = df_columns.index(placeholder_2)
        else:
            major_column = None
        if placeholder_3:
            honor_column = df_columns.index(placeholder_3)
        else:
            honor_column = None
        if placeholder_4:
            quote_column = df_columns.index(placeholder_4)
        else:
            quote_column = None
        if image_placeholder:
            image_column = df_columns.index(image_placeholder)
        else:
            image_column = None
        # print("NAME COLUMN INDEX IN CSV: ", name_column)

        with open(csv_path, "r") as csv_file:
            logger.info('====================CSV Processing Started====================')

            # Delete previous uploaded data from same file to avoid duplication
            # Decode and process the data
            decoded_file = csv_file.read()
            io_string = io.StringIO(decoded_file)
            count = 0
            # data_source = UploadedFiles.objects.get(file_name=csv_name, is_duplicated=False)
            data_source_id = data_source.id

            for line in csv.reader(io_string, delimiter=',', quotechar='"'):
                # print(line)
                if count == 0:
                    count += 1
                    continue
                else:
                    temp_obj = {"id": count}
                    if name_column or name_column == 0:
                        temp_obj["name"] = line[int(name_column)]
                        # print(temp_obj["name"])
                    else:
                        temp_obj["name"] = ""
                    if major_column:
                        temp_obj["major"] = line[int(major_column)]
                    else:
                        temp_obj["major"] = ""
                    # if school_column:
                    #     temp_obj["school"] = line[int(school_column)]
                    # else:
                    #     temp_obj["school"] = ""
                    if honor_column:
                        temp_obj["honor"] = line[int(honor_column)]
                    else:
                        temp_obj["honor"] = ""
                    if quote_column:
                        temp_obj["quote"] = line[int(quote_column)]
                    else:
                        temp_obj["quote"] = ""

                    if image_column and str(line[int(image_column)]).strip() != "":
                        temp_obj["image"] = convert_to_base64(str(line[int(image_column)]))
                    else:
                        temp_obj["image"] = ""
                        # print("converted image data : ", temp_obj.get("image"))
                    # else:
                    #     pass
                    #     im1 = Image.open(default_image_path)
                    #     #
                    #     # default_file_image_name = "media/" + str(default_image)
                    #     # im1.save(default_file_image_name)
                    #     logger.info("MIME : {0} ".format(im1.get_format_mimetype()))
                    #     with open(default_image_path, "rb") as temp_img:
                    #         temp_obj["image"] = "data:" + im1.get_format_mimetype() + ";" + "base64," + \
                    #                             str(base64.b64encode(temp_img.read()).decode("utf-8"))
                    #     im1.close()
                    temp_obj["Audio"] = ""
                    logger.info('Count:  {0} '.format(str(count)))
                    # logger.info(temp_obj)
                    SlidesData(
                        name=temp_obj["name"],
                        major=temp_obj["major"],
                        # school=temp_obj["school"],
                        honor=temp_obj["honor"],
                        image=temp_obj["image"],
                        audio=temp_obj["Audio"],
                        quote=temp_obj["quote"],
                        data_source_id=data_source_id
                    ).save()
                    count += 1

        data_source.status = 2
        data_source.save()

        logger.info('====================CSV Processing Finished====================')
        logger.info('Removing File:  1. {0}  \n \n '.format(
            str(csv_path)))

        os.remove(csv_path)
        # os.remove(default_image_path)
        # os.remove(bg_path)
        logger.info('====================Garbage Cleaning Done====================')
        return True
    except Exception as exc:
        data_source.status = 3
        data_source.save()
        print(exc)
        return False
