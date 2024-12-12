"""FilesUploader Module"""
import os
import files_sdk
from lib.credential_vault import CredentialVault


class FilesUploader:
    """Files Uploader Class"""
    destination_path = "/RLEC_Customers/Uploads"
    # destination_path = "/Uploads"

    @staticmethod
    def set_api_key():
        """Store API Key in Vault"""
        try:
            _junk, api_key = CredentialVault.decrypt_credentials(".api.key")
            files_sdk.set_api_key(api_key)
        except Exception as e:
            raise Exception("API Key") from e

    @staticmethod
    def upload_file(source_file):
        """Upload source_file """
        fname = os.path.basename(source_file)
        remote_file = os.path.join(FilesUploader.destination_path, fname)
        FilesUploader.set_api_key()
        try:
            files_sdk.file.upload_file(source_file, remote_file)
        except Exception as e:
            print(e)
            raise Exception("Upload Error") from e

    @staticmethod
    def upload_bytes(source_bytes, source_file):
        """Upload a string using source_file as destination name"""
        try:
            fname = os.path.basename(source_file)
            remote_file = os.path.join(FilesUploader.destination_path, fname)
            FilesUploader.set_api_key()
            with files_sdk.open(remote_file, "wb") as f:
                f.write(source_bytes)
        except Exception as e:
            print(e)
            raise Exception("Upload Error") from e
