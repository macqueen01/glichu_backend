from celery import shared_task, result
import ipfshttpclient

import subprocess
import os
import shutil

from django.apps import apps


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

    args = [
        'ffmpeg',
        '-i',
        f'{input}',
        '-vcodec',
        'libx264',
        '-acodec',
        'aac',
        '-vf',
        'setsar=1',
        '-vf',
        """scale='min(370, iw):-1'""",
        f'{output}'
    ]

    process = subprocess.Popen(
        args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    (out, err) = process.communicate('')

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
    creates a sequence of images taken inbetween the given framerate.
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

    args = [
        'ffmpeg',
        '-i',
        f'{input}',
        '-qscale:v',
        f'{quality}',
        '-vf',
        f'fps={fps}',
        f'{output_dir}/%d.jpeg'
    ]

    process = subprocess.Popen(
        args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    (out, err) = process.communicate('')

    if process.returncode != 0:
        shutil.rmtree(output_dir)
        return False

    return output_dir


@shared_task
def upload_to_ipfs(dirname, scrolls_id):

    scrolls_model = apps.get_model(
        app_label='main', model_name='Scrolls', require_ready=True)


    if not os.path.exists(dirname):
        return False

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

    scrolls_model = apps.get_model(
        app_label='main', model_name='Scrolls', require_ready=True)

    if not os.path.exists(dirname):
        return False

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



