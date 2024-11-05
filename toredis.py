import argparse
import os
from TarProcessor import TarProcessor
from FilesUploader import FilesUploader
from Logger import Logger

logger = Logger(name='MyLogger', facility='toredis', log_to_file=False, filename='logs/app')
# Set up argument parser
parser = argparse.ArgumentParser(description="Print the filename of a specified file.")
parser.add_argument("file", help="Path to the file")
parser.add_argument("--bloat", action="store_true", help="Enable bloat mode")

# Parse the arguments
args = parser.parse_args()

# Extract and print the filename
filename = os.path.basename(args.file)
print(f"Filename: {filename}")

file_bytes = None
upload_bytes = None

# Read the file in binary mode and store it as bytes
try:
    with open(args.file, "rb") as f:
        file_bytes = f.read()
except FileNotFoundError:
    print("Error: File not found.")
except IOError:
    print("Error: Could not read the file.")

# Check if the bloat flag is set
if not args.bloat:
    tar_processor_bytes = TarProcessor()                
    savings, original_size, new_size, upload_bytes = tar_processor_bytes.process_from_bytes(file_bytes)
    logger.info(f"Original tar size: {original_size}MB")
    logger.info(f"New tar size: {new_size}MB")
    logger.info(f":Storage savings: {savings}MB")
else:
    upload_bytes = file_bytes

logger.info(f"Uploading {filename}to Redis.io")

FilesUploader.upload_bytes(file_bytes,filename)
