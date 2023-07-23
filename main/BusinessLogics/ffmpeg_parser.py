import os
import shutil
import subprocess


# All Ffmpeg execution functions will return 
# (process, (out, err))


def codec_converter(input_path, output_path, test = True):

    """
    Codec conversion
    """

    args1 = [
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
        """scale='min(500, iw):-1'""",
        '-vf',
        'fps=20',
        f'{output_path}'
    ]

    """
    Test Codec conversion
    """

    args2 = [
        'ffmpeg',
        '-i',
        f'{input_path}',
        '-c:v', 'libx264',  # Video codec
        '-crf', '23',       # Constant Rate Factor (lower values result in higher quality)
        '-preset', 'medium', # Preset for encoding speed and efficiency (e.g., ultrafast, veryslow)
        '-vf', 'scale=740:-2',  # Video resolution (e.g., width: 1280, height: maintain aspect ratio)
        '-c:a', 'aac',      # Audio codec
        '-b:a', '192k',     # Audio bitrate
        '-vf', 'setsar=1',  # Sample aspect ratio
        f'{output_path}'
    ]

    if test:
        args = args2
    else:
        args = args1

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
        f'{input_path}',
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

    if output_dir[-1] == '/':
        output_dir = output_dir[:-1]


    
    args = [
        'ffmpeg',
        '-f',
        'concat',
        '-safe',
        '0',
        '-i',
        f'{txt_file_path}',
        f'{output_dir}/{filename}'
    ]

    process = subprocess.Popen(
        args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    (out, err) = process.communicate('')


    return (process, (out, err))




