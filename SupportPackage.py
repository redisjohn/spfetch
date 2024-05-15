import os
from datetime import datetime
import requests

class SupportPackage:

    

    @staticmethod
    def get_fname(fqdn,path):
            current_time = datetime.now()
            formatted_time = current_time.strftime("%Y%m%d%H%M%S")            
            fname = f"{fqdn}_{formatted_time}.tar.gz"
            if not os.path.exists(path):
                os.makedirs(path)
            return os.path.join(path,fname)

    @staticmethod
    def download_package(fqdn, username, password,path):
        try:
            requests.packages.urllib3.disable_warnings()
            download_url = "https://" + fqdn + ":9443/v1/debuginfo/all"
            print("Starting Download")        
            response = requests.get(download_url, auth=(username, password), verify=False)
            response.raise_for_status()
            fname = SupportPackage.get_fname(fqdn,path)            
            with open(fname, "wb") as f:
                f.write(response.content)
            print(f"Support package for {fqdn} downloaded successfully.")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading support package for {fqdn}: {e}")
