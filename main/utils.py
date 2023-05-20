import tarfile
import os

def create_tar_archive_with_parent_basename(source_dir, dest_file, parent_basename, compression_mode="w"):
    # check if source dir does not exist
    if not os.path.exists(source_dir):
        return False
    
    # check if dest file already exists
    if os.path.exists(dest_file):
        return False

    with tarfile.open(dest_file, compression_mode) as tar:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                path = os.path.join(root, file)
                arcname = os.path.join(parent_basename, os.path.relpath(path, source_dir))
                tar.add(path, arcname=arcname)
    
    return dest_file



