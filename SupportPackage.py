import os
from datetime import datetime
import requests
import json

class SupportPackage:

    @staticmethod
    def get_fname(fqdn,path):
            current_time = datetime.now()
            formatted_time = current_time.strftime("%Y%m%d%H%M%S")            
            fname = f"debuginfo.{fqdn}_{formatted_time}.tar.gz"
            if not os.path.exists(path):
                os.makedirs(path)
            return os.path.join(path,fname)

    @staticmethod
    def tablulate_bdb_info(fqdn,response):

        bdb_json = json.loads(response)

        #sort by uid
        bdb_names = sorted(bdb_json, key=lambda x: x['uid'])

        # column width for tablular format
        name_width = max(len(bdb['name']) for bdb in bdb_names) + 2
        uid_width = max(len(str(bdb['uid'])) for bdb in bdb_names) + 2
        version_width = max(len(str(bdb['version'])) for bdb in bdb_names) + 2
        shards_width = max(len(str(bdb['shards_count'])) for bdb in bdb_names) + 2

        print('\n' + fqdn)
        print(f"{'Id'.ljust(uid_width)} {'Name'.ljust(name_width)} {'Version'.ljust(version_width)} {'Shards'.ljust(shards_width)}")
        print('-' * (uid_width + name_width + version_width + shards_width + 6))

        for bdb in bdb_names:
            if (bdb['slave_ha']):
                bdb['shards_count'] *= 2
            print(f"{str(bdb['uid']).ljust(uid_width)}  {str(bdb['name']).ljust(name_width)} {str(bdb['version']).ljust(version_width)} {str(bdb['shards_count']).rjust(shards_width)}")

    def deserialize_bdb_info(fqdn,response):
        bdb_info = []
        bdb_json = json.loads(response)
        for bdb in bdb_json:
            bdb['cluster'] = fqdn
            if (bdb['slave_ha']):
                bdb['shards_count'] *= 2
        #sort by uid
        bdb_names = sorted(bdb_json, key=lambda x: (x['cluster'], x['uid']))
        for bdb in bdb_names:
            del bdb['slave_ha']
            bdb_info.append(bdb)
        return bdb_info

    @staticmethod
    def get_bdb_names(fqdn,username,password):
        try:
            requests.packages.urllib3.disable_warnings()
            download_url = "https://" + fqdn + ":9443/v1/bdbs?fields=uid,name,version,shards_count,slave_ha"                 
            response = requests.get(download_url, auth=(username, password), verify=False)            
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error Getting Database Names for {fqdn}: {e}")                  

    @staticmethod
    def deserialize_license_info(fqdn,response):
        license = json.loads(response)
        output = {}
        output['cluster'] = fqdn 
        output['shards_limit'] = license['shards_limit']
        output['ram_shards'] = license['ram_shards_in_use']
        output['flash_shards'] = license['flash_shards_in_use']
        return output

    @staticmethod
    def get_license_info(fqdn,username,password):
        try:
            requests.packages.urllib3.disable_warnings()
            download_url = "https://" + fqdn + ":9443/v1/license"                 
            response = requests.get(download_url, auth=(username, password), verify=False)            
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error License Info for {fqdn}: {e}")                  
        
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
