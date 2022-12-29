from celery import shared_task, result
import subprocess
import os

from main.models import User, Scrolls, Cell

@shared_task
def convert(input, output):

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

    return out.__str__()

@shared_task
def scrollify(input, output_dir, fps, quality = 5, scrolls_id = None):
    """
    Scrollify takes a converted mp4 video as an input and 
    creates a sequence of images taken inbetween the given framerate.
    Scrollify then calls the scroll with the given scrolls_id, writes the cell objects,
    and then saves them.

    Scrollify should be called AFTER the creation of the scrolls object of given id.
    """

    output_dir = os.path.dirname(output_dir)

    if not os.path.exists(input):
        return False
    
    if os.path.exists(output_dir):
        return False
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # quality should be in range of 1 ~ 31, from 1 being best to 31 being worst
    assert((0 < quality) and (quality <= 31), True)


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

    return out.__str__()
    
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
