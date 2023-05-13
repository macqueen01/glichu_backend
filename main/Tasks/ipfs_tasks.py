from celery import shared_task, result
import ipfshttpclient

import subprocess
import os

from django.apps import apps

from main.BusinessLogics import models

# IPFS interaction tasks

@shared_task
def upload_to_ipfs(dirname, scrolls_id):

    if not os.path.exists(dirname):
        return False

    models.SCROLLS_MODEL.objects.initialize(scrolls_id)

    if scrolls := models.SCROLLS_MODEL.objects.get_scrolls_from_id(scrolls_id):

        try: 
            client = ipfshttpclient.connect()
            hashes = []

            for file in os.listdir(dirname):
                basename = os.path.basename(file)
                index = int(os.path.splitext(basename)[0]) - 1

                file_path = os.path.join(dirname, file)
                res = client.add(file_path)
                hashes.append(res)

                cell = models.SCROLLS_MODEL.objects.create_cell(
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

                cell = models.SCROLLS_MODEL.objects.create_cell(
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

    models.SCROLLS_MODEL.objects.initialize(scrolls_id)

    if scrolls := models.SCROLLS_MODEL.objects.get_scrolls_from_id(scrolls_id):
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