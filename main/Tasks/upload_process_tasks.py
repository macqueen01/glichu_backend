from celery import shared_task, result
import ipfshttpclient

import subprocess
import os
import shutil

from django.apps import apps

from main.BusinessLogics import ffmpeg_parser, models




@shared_task
def convert(input, output, media_id):

    output_dir = os.path.dirname(output)

    if not os.path.exists(input):
        return False

    if os.path.exists(output):
        return False

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Now start converting

    process, (_, _) = ffmpeg_parser.codec_converter(input, output_dir)

    if process.returncode != 0:
        shutil.rmtree(output)
        return False

    if media_id:
        # Saves the converted media path if media id is given.
        media_object = models.MEDIA_MODEL.objects.get(id__exact=media_id)
        media_object.url_postprocess = output
        media_object.save()

    return media_id.__str__()


@shared_task
def scrollify(input, output_dir, fps, quality=5):
    """
    Scrollify takes a converted mp4 video as an input and 
    creates a sequence of images taken in-between the given frame rate.
    Scrollify then calls the scroll with the given scrolls_id, writes the cell objects,
    and then saves them.

    Scrollify should be called AFTER the creation of the scrolls object of given id.
    """

    if not os.path.exists(input):
        return False

    if os.path.exists(output_dir):
        return False

    # quality should be in range of 1 ~ 31, from 1 being best to 31 being worst
    if quality < 1 or quality > 31:
        return False
    
    os.makedirs(output_dir)

    # Now start producing thumbnails

    process, (_, _) = ffmpeg_parser.slice_to_images(input, output_dir, fps, quality)

    if process.returncode != 0:
        shutil.rmtree(output_dir)
        return False

    return output_dir