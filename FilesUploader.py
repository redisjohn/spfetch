import files_sdk
from files_sdk import File
from Logger import Logger
import os
from CredentialVault import CredentialVault

class FilesUploader:

    destination_path = "/RLEC_Customers/Uploads"  
    #destination_path = "/Uploads"

    @staticmethod
    def set_api_key():
        try:
            junk, api_key = CredentialVault.decrypt_credentials(".api.key")
            files_sdk.set_api_key(api_key)
        except Exception as e:
            print(e)
            raise Exception("API Key") from e

    @staticmethod
    def upload_file(source_file):
        fname = os.path.basename(source_file)
        remote_file = os.path.join(FilesUploader.destination_path,fname)
        FilesUploader.set_api_key()
        try: 
            files_sdk.file.upload_file(source_file,remote_file)
        except Exception as e:
            raise Exception("Upload Error") from e
       
    @staticmethod 
    def upload_bytes(source_bytes,fname):
        try:
            remote_file = os.path.join(FilesUploader.destination_path,fname)
            with files_sdk.open(remote_file, "wb") as f:
                f.write(source_bytes)            
        except Exception as e:
            raise Exception("Upload Error") from e 

'''
if __name__ == "__main__":

    FilesUploader.set_api_key('0cd9b99aec72c2d9e5dc0827deee3fb03cfc574dcc75cab45d39668fd8e9f284')
    FilesUploader.upload_file('output/d.tar.gz')

    fname = os.path.basename("output/d.tar.gz.1")

    with open("output/d.tar.gz.1", "rb") as file:
        contents = file.read()
        FilesUploader.upload_bytes(contents,fname)
'''    