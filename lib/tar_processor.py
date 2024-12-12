"""tar processor module"""
import tarfile
import os
import io


def divide_and_round(number):
    """divide and round"""
    result = number / 1_000_000
    return round(result, 2)


class TarProcessor:
    """tar processor class"""

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
                    if member.name.endswith(
                            '.gz') or member.name in self.exclude_files:
                        # print(f"Excluding file: {member.name}")
                        continue

                    # Extract the file content
                    file_obj = original_tar.extractfile(member)
                    if file_obj:
                        content = file_obj.read()

                        # Check if it's a .log file and truncate to the last
                        # 100 lines if so
                        if member.name.endswith('.log'):
                            try:
                                content_str = content.decode('utf-8')
                                truncated_content = self.tail_file(content_str)
                                content = truncated_content.encode('utf-8')
                            except UnicodeDecodeError:
                                print(
                                    f"Warning: Failed to decode {member.name} as UTF-8.")

                        # Add the file to the new tar file
                        new_member = tarfile.TarInfo(name=member.name)
                        new_member.size = len(content)
                        new_tar.addfile(
                            new_member, fileobj=io.BytesIO(content))

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
                    if member.name.endswith(
                            '.gz') or member.name in self.exclude_files:
                        # print(f"Excluding file: {member.name}")
                        continue

                    # Extract the file content
                    file_obj = original_tar.extractfile(member)
                    if file_obj:
                        content = file_obj.read()

                        # Check if it's a .log file and truncate to the last
                        # 100 lines if so
                        if member.name.endswith('.log'):
                            try:
                                content_str = content.decode('utf-8')
                                truncated_content = self.tail_file(content_str)
                                content = truncated_content.encode('utf-8')
                            except UnicodeDecodeError:
                                print(
                                    f"Warning: Failed to decode {member.name} as UTF-8.")

                        # Add the file to the new tar file
                        new_member = tarfile.TarInfo(name=member.name)
                        new_member.size = len(content)
                        new_tar.addfile(
                            new_member, fileobj=io.BytesIO(content))

        # Get the size of the new tar data in bytes
        new_size = destination_io.tell()
        storage_savings = original_size - new_size

        # Return to the start of the BytesIO object for further use
        destination_io.seek(0)

        return divide_and_round(storage_savings), divide_and_round(
            original_size), divide_and_round(new_size), destination_io.getvalue()
