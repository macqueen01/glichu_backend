import boto3
import os
from rest_framework.settings import api_settings
from storages.backends.s3boto3 import S3Boto3Storage
from django.core.files.storage import FileSystemStorage


class LocalStorage(FileSystemStorage):
    def __init__(self, location=None, base_url=None, file_permissions_mode=None, directory_permissions_mode=None):
        super().__init__(location=location, base_url=base_url, file_permissions_mode=file_permissions_mode, directory_permissions_mode=directory_permissions_mode)

class S3Storage(S3Boto3Storage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

def download_files_from_s3(client, bucket_name, s3_directory, temp_root):
    files = []
    response = client.list_objects_v2(Bucket=bucket_name, Prefix=s3_directory)

    if 'Contents' not in response:
        print("No files found in the specified S3 directory.")
        return
        
    local_dir = os.path.join(temp_root, f'{s3_directory}')
    os.makedirs(local_dir, exist_ok=True)

    for obj in [obj['Key'] for obj in response['Contents'] if os.path.splitext(obj['Key'])[-1] == '.jpeg']:
        file_path = obj
        file_name = obj.split('/')[-1]
        local_file = os.path.join(local_dir, f'{file_name}')        
        
        # Download the file from S3 to local storage
        client.download_file(bucket_name, file_path, local_file)
        files.append(local_file)
    
    files.sort(key=lambda x: int(os.path.splitext(x)[0].split('/')[-1]))
    return files


    