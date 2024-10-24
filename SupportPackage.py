import os
from datetime import datetime
import requests
import json

class SupportPackage:

    @staticmethod
    def convert_zulu_string(date_string):
        date_object = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
        formatted_date = date_object.strftime("%Y-%m-%d")
        return formatted_date


    @staticmethod
    def get_fname(fqdn,path):
            current_time = datetime.now()
            formatted_time = current_time.strftime("%Y%m%d%H%M%S")            
            fname = f"debuginfo.{fqdn}_{formatted_time}.tar.gz"
            if not os.path.exists(path):
                os.makedirs(path)
            return os.path.join(path,fname)

    @staticmethod
    def summarize_node_info(response):
        node_info = {}
        version_mismatch = False
        os_mismatch = False
        node_count = 0
        version = ''
        os_version = ''
        nodes_json = json.loads(response)
        for node in nodes_json:
            if (node_count == 0):
                version = node['software_version']
                os_version = node['os_version']
                node_count = 1
            else:
                node_count += 1
                if version != node['software_version']:
                    version_mismatch = True
                if os_version != node['os_version']:
                    os_mismatch = True

        node_info['nodes'] = node_count
        node_info['version'] = version 
        node_info['os'] = os_version 
        node_info['mismatch'] = True if (os_mismatch | version_mismatch) else False
        return node_info
    
    @staticmethod
    def get_nodes(fqdn,username,password):
        try:
            requests.packages.urllib3.disable_warnings()
            download_url = "https://" + fqdn + ":9443/v1/nodes"                 
            response = requests.get(download_url, auth=(username, password), verify=False)            
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error Getting Node Informationfor {fqdn}: {e}")                  


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
        bdbs  = []
        bdb_json = sorted(json.loads(response) , key=lambda x: (x['uid']))
        
        for bdb in bdb_json:

            rec = {}
            rec['Id'] = bdb['uid']
            rec['Name'] = bdb['name']
            rec['Version'] = bdb['version']
            rec['Total Shards'] = bdb['shards_count'] if not bdb['slave_ha'] else bdb['shards_count'] * 2
            rec['High Availability'] = bdb['slave_ha']
            rec['Flex'] = bdb['bigstore'] 
            rec['Created'] = SupportPackage.convert_zulu_string(bdb['created_time'])
            rec['Modified'] = SupportPackage.convert_zulu_string(bdb['last_changed_time'])
            rec['Persistence'] = bdb['data_persistence']
            rec['Eviction Policy'] = bdb['eviction_policy']
            rec['CRDB'] = bdb['crdt']
            rec['Modules'] = ''
            for module in bdb['module_list']:
                rec['modules'] += (module + ' ')
            rec['TLS'] = bdb['ssl']            
            rec['OSS Cluster API'] = bdb['oss_cluster']
            rec['Proxy Policy'] = bdb['proxy_policy']
            rec['Shard Placement'] = bdb['shards_placement']

            bdbs.append(rec) 

        return bdbs
    

    @staticmethod
    def get_bdb_names(fqdn,username,password):
        try:
            requests.packages.urllib3.disable_warnings()
            #download_url = "https://" + fqdn + ":9443/v1/bdbs?fields=uid,name,version,shards_count,slave_ha"                 
            download_url = "https://" + fqdn + ":9443/v1/bdbs"                 
            response = requests.get(download_url, auth=(username, password), verify=False)            
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error Getting Database Names for {fqdn}: {e}")                  


    @staticmethod
    def deserialize_license_info(fqdn,response):
        license = json.loads(response)
        return license
    
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
