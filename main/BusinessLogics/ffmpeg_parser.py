import os
import shutil
import subprocess


# All Ffmpeg execution functions will return 
# (process, (out, err))


def codec_converter(input_path, output_path):

    """
    Codec conversion
    """

    args = [
        'ffmpeg',
        '-i',
        f'{input_path}',
        '-vcodec',
        'libx264',
        '-acodec',
        'aac',
        '-vf',
        'setsar=1',
        '-vf',
        """scale='min(370, iw):-1'""",
        f'{output_path}'
    ]

    process = subprocess.Popen(
        args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    (out, err) = process.communicate('')

    return (process, (out, err))

def slice_to_images(input_path, output_dir, fps, quality):


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

    return (process, (out, err))


def execute_from_txt_file(txt_file_path, output_dir, filename):
    
    args = [
        'ffmpeg',
        '-f',
        'concat',
        '-safe',
        '0',
        '-i',
        f'{txt_file_path}',
        '-c',
        'copy',
        f'{output_dir}/{filename}.mp4'
    ]

    process = subprocess.Popen(
        args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    (out, err) = process.communicate('')


    return (process, (out, err))




