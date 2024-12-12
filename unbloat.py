#!/usr/bin/env python3
'''unbloat - a utility to manipulate support packages'''

import argparse
import os
from pathlib import Path
from lib.TarProcessor import TarProcessor
from lib.FilesUploader import FilesUploader
from lib.Logger import Logger

logger = Logger(
    name="MyLogger", facility="unbloat", log_to_file=False, filename="logs/app"
)
# Set up argument parser
parser = argparse.ArgumentParser(
    description="Remove Bloat from Support Packages")
parser.add_argument("file", help="Path to the file")
parser.add_argument("--bloat", action="store_true", help="Leave it Bloated")
parser.add_argument("--upload", action="store_true", help="upload to redis.io")
parser.add_argument("--nosave", action="store_true", help="Do not save")

# Parse the arguments
args = parser.parse_args()

# Extract and print the filename
filename = os.path.basename(args.file)
print(f"Filename:({filename})")

FILE_BYTES = None
UPLOAD_BYTES = None
NOSAVE = False

# Read the file in binary mode and store it as bytes
try:
    with open(args.file, "rb") as f:
        FILE_BYTES = f.read()
except FileNotFoundError as e:
    logger.exception(e, "Error: File not found.")
except IOError:
    print("Error: Could not read the file.")


# Check if the bloat flag is set
if not args.bloat:
    NOSAVE = args.nosave
    tar_processor_bytes = TarProcessor()
    savings, original_size, new_size, UPLOAD_BYTES = (
        tar_processor_bytes.process_from_bytes(FILE_BYTES)
    )
    logger.info(f"Original tar size: {original_size}MB")
    logger.info(f"New tar size: {new_size}MB")
    logger.info(f":Storage savings: {savings}MB")
else:
    UPLOAD_BYTES = FILE_BYTES
    NOSAVE = True

if args.upload:
    logger.info(f"Uploading {filename} to Redis.io")
    FilesUploader.upload_bytes(FILE_BYTES, filename)

if NOSAVE is False:
    file_path = Path(args.file)
    drive = file_path.drive  # Drive (empty on Linux, e.g., "C:" on Windows)
    fname = file_path.stem  # Filename without extension
    extension = file_path.suffix  # File extension with the dot (.)

    new_filename = Path(drive, file_path.parent, f"unbloat-{fname}" + extension)

    try:
        logger.info(f"Save:{new_filename}")
        with open(new_filename, "wb") as f:
            f.write(FILE_BYTES)
    except FileNotFoundError as e:
        logger.exception(e, "Error: File not found.")
    except IOError as e:
        logger.exception(e, "Error: Could not write the file.")
