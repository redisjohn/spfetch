import tarfile
import os
import io

class TarProcessor:
 
    def __init__(self, source_tar="", destination_tar="", exclude_files=None):
        """
        Initialize the TarProcessor class.
        :param source_tar: Path to the original tar file.
        :param destination_tar: Path to the new tar file.
        :param exclude_files: A list of files (with paths) to be excluded.
        """
        self.lines_to_tail = 500
        self.source_tar = source_tar
        self.destination_tar = destination_tar
        self.exclude_files = exclude_files if exclude_files else []
    
    def tail_file(self, content):
        """
        Get the last n lines from a text content.
        
        :param content: The text content of the file.
        :return: The truncated content containing the last 100 lines.
        """
        lines = content.splitlines()
        return "\n".join(lines[-self.lines_to_tail:])

    def process_from_file(self):
        """
        Copy contents of the source tar file to a new tar file.
        Excludes specific files and truncates .log files to the last 100 lines.
        Excludes any .gz files found inside the tar file.

        :return: A tuple containing storage savings, original size, and new size.
        """
        with tarfile.open(self.source_tar, 'r:*') as original_tar:
            with tarfile.open(self.destination_tar, 'w:gz') as new_tar:
                for member in original_tar.getmembers():
                    # Exclude .gz files or files in the exclude_files list
                    if member.name.endswith('.gz') or member.name in self.exclude_files:
                        #print(f"Excluding file: {member.name}")
                        continue

                    # Extract the file content
                    file_obj = original_tar.extractfile(member)
                    if file_obj:
                        content = file_obj.read()
                        
                        # Check if it's a .log file and truncate to the last 100 lines if so
                        if member.name.endswith('.log'):
                            try:
                                content_str = content.decode('utf-8')
                                truncated_content = self.tail_file(content_str)
                                content = truncated_content.encode('utf-8')
                            except UnicodeDecodeError:
                                print(f"Warning: Failed to decode {member.name} as UTF-8.")
                        
                        # Add the file to the new tar file
                        new_member = tarfile.TarInfo(name=member.name)
                        new_member.size = len(content)
                        new_tar.addfile(new_member, fileobj=io.BytesIO(content))
        
        # Calculate storage savings
        original_size = os.path.getsize(self.source_tar)
        new_size = os.path.getsize(self.destination_tar)
        storage_savings = original_size - new_size

        return storage_savings, original_size, new_size


    def process_from_bytes(self, source_bytes):
        """
        Process the source tar data from a bytes object instead of a file.
        
        :param source_bytes: A bytes object representing a tar archive.
        :return: A tuple containing storage savings, original size, and new size.
        """
        original_size = len(source_bytes)
        
        # Create a BytesIO object from the source bytes
        source_io = io.BytesIO(source_bytes)
        
        # Open the source tar file from bytes
        with tarfile.open(fileobj=source_io, mode='r:*') as original_tar:
            # Prepare a BytesIO object to hold the new tar data
            destination_io = io.BytesIO()
            
            with tarfile.open(fileobj=destination_io, mode='w:gz') as new_tar:
                for member in original_tar.getmembers():
                    # Exclude .gz files or files in the exclude_files list
                    if member.name.endswith('.gz') or member.name in self.exclude_files:
                        print(f"Excluding file: {member.name}")
                        continue

                    # Extract the file content
                    file_obj = original_tar.extractfile(member)
                    if file_obj:
                        content = file_obj.read()
                        
                        # Check if it's a .log file and truncate to the last 100 lines if so
                        if member.name.endswith('.log'):
                            try:
                                content_str = content.decode('utf-8')
                                truncated_content = self.tail_file(content_str)
                                content = truncated_content.encode('utf-8')
                            except UnicodeDecodeError:
                                print(f"Warning: Failed to decode {member.name} as UTF-8.")
                        
                        # Add the file to the new tar file
                        new_member = tarfile.TarInfo(name=member.name)
                        new_member.size = len(content)
                        new_tar.addfile(new_member, fileobj=io.BytesIO(content))
        
        # Get the size of the new tar data in bytes
        new_size = destination_io.tell()
        storage_savings = original_size - new_size

        # Return to the start of the BytesIO object for further use
        destination_io.seek(0)

        return storage_savings, original_size, new_size, destination_io.getvalue()


'''
# Example usage
if __name__ == "__main__":
    # Specify the source and destination tar file paths
    source_tar_path = 'example.tar.gz'
    destination_tar_path = 'example_filtered.tar.gz'

    # List of files to exclude (use exact paths as they appear in the tar file)
    files_to_exclude = [
        'file_to_remove.txt',
        'folder/subfolder/file_to_exclude.txt'
    ]

    # Create an instance of TarProcessor
    tar_processor = TarProcessor(source_tar_path, destination_tar_path, files_to_exclude)

    # Perform the exclusion and truncation
    savings, original_size, new_size = tar_processor.exclude_and_truncate()

    print(f"Original tar file size: {original_size} bytes")
    print(f"New tar file size: {new_size} bytes")
    print(f"Storage savings: {savings} bytes")

    # Example with bytes input
    with open(source_tar_path, 'rb') as f:
        tar_bytes = f.read()
    
    # Create an instance of TarProcessor for bytes-based processing
    tar_processor_bytes = TarProcessor(exclude_files=files_to_exclude)
    savings, original_size, new_size, new_tar_bytes = tar_processor_bytes.process_from_bytes(tar_bytes)
    print(f"(Bytes) Original tar size: {original_size} bytes")
    print(f"(Bytes) New tar size: {new_size} bytes")
    print(f"(Bytes) Storage savings: {savings} bytes")
    
    # Optionally save the new bytes to a file
    with open('example_filtered_from_bytes.tar.gz', 'wb') as f:
        f.write(new_tar_bytes)

'''

