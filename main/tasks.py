from celery import shared_task, result
import ipfshttpclient

import subprocess
import os
import shutil

from django.apps import apps

from main.BusinessLogics import ffmpeg_parser
from main.BusinessLogics.Scrolls.timelines import IndexTimeline
from main.BusinessLogics.Scrolls.timelines import Remix as RemixInMemory
from mockingJae_back.storages import download_files_from_s3
from mockingJae_back import settings
from mockingJae_back.celery import app

@shared_task
def remix_to_video(json):

    timeline_json = json['timeline']['first']
    title = json['title']
    length = json['length']
    scrolls = json['scrolls']
    scrolls_id = int(scrolls.split('_')[0])

    timeline = IndexTimeline(
        timeline_json=timeline_json,
        length=length,
    )
    
    remix = RemixInMemory(
        title = title,
        timeline=timeline,
        scrolls_id=scrolls_id,
    )

    output_path = os.path.join(
                settings.MEDIA_ROOT, 
                f'auto_recordings/{remix.get_scrolls().id}/{remix.get_title()}'
            )

    remix_model = apps.get_model(
            app_label='main', model_name='Remix', require_ready=True)

    # sort the files in the scrolls_dir and then create a list of files

    if remix.get_scrolls().scrolls_dir.split('/')[-1] == '':
        scrolls_name = remix.get_scrolls().scrolls_dir.split('/')[-2]
        image_sequences_dir = remix.get_scrolls().scrolls_dir.split('/')[-3]
    else:
        scrolls_name = remix.get_scrolls().scrolls_dir.split('/')[-1]
        image_sequences_dir = remix.get_scrolls().scrolls_dir.split('/')[-2]
        
    scrolls_dir = f'{image_sequences_dir}/{scrolls_name}/'
    output_dir = f'{os.path.dirname(output_path)}/'
    
    remix_name = remix.get_title()

    # if the output path already exists, add a number to the end of the file until it doesn't exist
    i = 1
    while os.path.exists(output_path):
        output_path = f'{output_dir}{remix_name.split(".")[0]}{i}.mp4'
        i += 1
    
    remix_name = output_path.split('/')[-1]

    os.makedirs(output_dir, exist_ok=True)

    files = download_files_from_s3(settings.s3_client, os.environ.get('AWS_STORAGE_BUCKET_NAME'), scrolls_dir, settings.TEMP_ROOT)

    # Now create ffmpegTemp in output_dir so that we can write the command on the file then refer it when ffmpeg task
    ffmpegTemp = os.path.join(output_dir, 'ffmpegTemp.txt')

    current_timestamp = remix.get_timeline().sentinel

    while current_timestamp.next:
        next_stamp = current_timestamp.next

        image_path = files[current_timestamp.index]
        timegap = (next_stamp.datetime - current_timestamp.datetime).total_seconds()
        timegap = str(format(timegap, ".6f"))

        with open(ffmpegTemp, 'a') as f:
            f.write(f'file \{image_path}\n')
            f.write(f'duration {timegap}\n')

        current_timestamp = next_stamp
    
    # Now start converting

    process, (out, err) = ffmpeg_parser.execute_from_txt_file(ffmpegTemp, output_dir, remix_name)

    if process.returncode != 0:
        os.remove(output_path)
        os.remove(ffmpegTemp)
        return False

    os.remove(ffmpegTemp)
    # removes the scrolls_dir from the temporary directory
    shutil.rmtree(f'{settings.TEMP_ROOT}/{scrolls_dir}')

    remix_obj = remix_model.objects.create_remix(
        title = remix_name, 
        scrolls = remix.get_scrolls(),
        remix_directory = output_path,
        )

    return remix_obj.__str__()

# scrolls uploading tasks

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

    process, (_, _) = ffmpeg_parser.codec_converter(input, output)

    if process.returncode != 0:
        shutil.rmtree(output)
        return False

    if media_id:
        # Saves the converted media path if media id is given.
        media_model = apps.get_model(
            app_label='main', model_name='VideoMedia', require_ready=True)
        media_object = media_model.objects.get(id__exact=media_id)
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


# ipfs uploader


@shared_task
def upload_to_ipfs(dirname, scrolls_id):

    if not os.path.exists(dirname):
        return False

    scrolls_model = apps.get_model(
            app_label='main', model_name='Scrolls', require_ready=True)
    scrolls_model.objects.initialize(scrolls_id)

    if scrolls := scrolls_model.objects.get_scrolls_from_id(scrolls_id):

        try: 
            client = ipfshttpclient.connect()
            hashes = []

            for file in os.listdir(dirname):
                basename = os.path.basename(file)
                index = int(os.path.splitext(basename)[0]) - 1

                file_path = os.path.join(dirname, file)
                res = client.add(file_path)
                hashes.append(res)

                cell = scrolls_model.objects.create_cell(
                    scrolls_id, res['Hash'], index)
                cell.save()
            
        except: 
            hashes = []

            for file in os.listdir(dirname):
                basename = os.path.basename(file)
                index = int(os.path.splitext(basename)[0]) - 1

                file_path = os.path.join(dirname, file)
                hash = ipfs_direct_call(file_path)
                hashes.append(hash)

                cell = scrolls_model.objects.create_cell(
                    scrolls_id, hash, index)
                cell.save()
            

        length = len(hashes)
        scrolls.length = length
        scrolls.uploaded = True
        scrolls.save()

        return scrolls.id

    return False

@shared_task
def upload_to_ipfs_as_a_directory(dirname, scrolls_id):
    """
    This method is called by upload_scrolls_directory which uploads the scrolls folder
    to ipfs as a directory.
    """

    if not os.path.exists(dirname):
        return False
    
    scrolls_model = apps.get_model(
            app_label='main', model_name='Scrolls', require_ready=True)

    scrolls_model.objects.initialize(scrolls_id)

    if scrolls := scrolls_model.objects.get_scrolls_from_id(scrolls_id):
        try: 
            client = ipfshttpclient.connect()
            res = client.add(dirname, recursive=True)
            hashes = res['Hash']
            scrolls.ipfs_hash = hashes
    
        except: 
            hashes = ipfs_direct_call(dirname)
            scrolls.ipfs_hash = hashes

    
        scrolls.length = len(os.listdir(dirname))
        scrolls.uploaded = True
        scrolls.save()
    
        return scrolls.id
    return False
                

def ipfs_direct_call(directory):
    args = [
        'ipfs',
        'add',
        '-r',
        directory
    ]

    process = subprocess.Popen(
        args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    (out, err) = process.communicate('')

    if process.returncode != 0:
        return False
    
    return out.__str__().split(' ')[-2]

# task health checker

def task_status(task_id):

    # PENDING --> 4
    # RUNNING --> 3
    # FAILURE --> 0
    # SUCCESS --> 1
    # TASK NOT FOUND --> 2

    if not task_id:
        return 2

    task = result.AsyncResult(task_id)

    if task.state == 'FAILURE':
        return 0

    elif task.state == 'RUNNING':
        return 3

    elif task.state == 'PENDING':
        return 4

    elif task.state == 'SUCCESS':
        return 1

    return 2


def get_result_from_task_id(task_id):

    if task_status(task_id) != 1:
        return False

    return result.AsyncResult(task_id).result

