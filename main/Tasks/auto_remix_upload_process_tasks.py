from celery import shared_task

import os
import shutil

from django.apps import apps

from main.BusinessLogics import ffmpeg_parser, models

@shared_task
def remix_to_video(output_dir, remix):

    # sort the files in the scrolls_dir and then create a list of files

    scrolls_dir = remix.get_scrolls().scrolls_dir

    if not os.path.exists(scrolls_dir):
        return False
    
    if os.path.exists(output_dir):
        return False
    
    os.makedirs(output_dir)

    files = os.listdir(scrolls_dir)
    files.sort()

    remix_name = remix.title

    # Now create ffmpegTemp in output_dir so that we can write the command on the file then refer it when ffmpeg task
    ffmpegTemp = os.path.join(output_dir, 'ffmpegTemp.txt')

    current_timestamp = remix.get_timeline().sentinel

    while current_timestamp.next:
        next_stamp = current_timestamp.next

        image_path = files[current_timestamp.index]
        timegap = next_stamp.timestamp - current_timestamp.timestamp
        # convert timestamp to milliseconds string
        timegap = str(int(timegap * 1000))

        with open(ffmpegTemp, 'a') as f:
            f.write(f'file \{image_path}\n')
            f.write(f'duration {timegap}\n')

        current_timestamp = next_stamp
    
    # Now start converting

    process, (_, _) = ffmpeg_parser.execute_from_txt_file(ffmpegTemp, output_dir, remix_name)

    if process.returncode != 0:
        shutil.rmtree(output_dir)
        return False

    # if successfully converted, delete the ffmpegTemp file
    os.remove(ffmpegTemp)

    remix_model = models.REMIX_MODEL.create_remix(
        title = remix_name, 
        scrolls = remix.get_scrolls(),
        remix_directory = output_dir,
        )
    
    remix_model.save()

    return remix_model.__str__()
