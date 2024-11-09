#!/usr/bin/env python3
import argparse
import os
from lib.TarProcessor import TarProcessor
from lib.FilesUploader import FilesUploader
from lib.Logger import Logger
from pathlib import Path

logger = Logger(name='MyLogger', facility='unbloat', log_to_file=False, filename='logs/app')
# Set up argument parser
parser = argparse.ArgumentParser(description="Remove Bloat from Support Packages")
parser.add_argument("file", help="Path to the file")
parser.add_argument("--bloat", action="store_true", help="Leave it Bloated")
parser.add_argument("--upload", action="store_true", help="upload to redis.io")
parser.add_argument("--nosave", action="store_true", help="Do not save")

# Parse the arguments
args = parser.parse_args()

# Extract and print the filename
filename = os.path.basename(args.file)
print(f"Filename:({filename})")

file_bytes = None
upload_bytes = None
nosave = False

# Read the file in binary mode and store it as bytes
try:
    with open(args.file, "rb") as f:
        file_bytes = f.read()
except FileNotFoundError as e:
    logger.exception(e,"Error: File not found.")
except IOError:
    print("Error: Could not read the file.")


# Check if the bloat flag is set
if not args.bloat:
    nosave = args.nosave 
    tar_processor_bytes = TarProcessor()                
    savings, original_size, new_size, upload_bytes = tar_processor_bytes.process_from_bytes(file_bytes)
    logger.info(f"Original tar size: {original_size}MB")
    logger.info(f"New tar size: {new_size}MB")
    logger.info(f":Storage savings: {savings}MB")    
else:
    upload_bytes = file_bytes
    nosave = True    

if args.upload:
    logger.info(f"Uploading {filename} to Redis.io")
    FilesUploader.upload_bytes(file_bytes,filename)

if nosave is False:
    file_path = Path(args.file)
    drive = file_path.drive              # Drive (empty on Linux, e.g., "C:" on Windows)
    path = str(file_path.parent)         # Parent directory (folder path)
    fname = file_path.stem            # Filename without extension
    extension = file_path.suffix         # File extension with the dot (.)

    new_filename = Path(drive,path,f"unbloat-{fname}" + extension) 

    try:
        logger.info(f"Save:{new_filename}")
        with open(new_filename, "wb") as f:
            f.write(file_bytes)
    except FileNotFoundError as e:
        logger.exception(e,"Error: File not found.")
    except IOError as e:
        logger.exception(e,"Error: Could not write the file.")
