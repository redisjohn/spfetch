import os
from datetime import datetime
import requests
import json
from TarProcessor import TarProcessor
from Logger import Logger

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
    def get_nodes(logger,fqdn,username,password):
        try:
            requests.packages.urllib3.disable_warnings()
            download_url = "https://" + fqdn + ":9443/v1/nodes"                 
            response = requests.get(download_url, auth=(username, password), verify=False)            
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logger.exception(e,f"Error Getting Node Information{fqdn}")                  


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
            print(f"({fqdn}):Error Getting Database Names")                  

    @staticmethod
    def deserialize_license_info(fqdn,response):
        license = json.loads(response)
        output = {}
        output['cluster'] = fqdn 
        output['expired'] = license['expired']
        output['expiration'] = SupportPackage.convert_zulu_string(license['expiration_date'])
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
    def download_package(logger,fqdn, username, password,path,db,reduce_tar_size):
        try:
            requests.packages.urllib3.disable_warnings()
            if db != 0:
                download_url = f"https://" + fqdn + ":9443/v1/debuginfo/node/bdb/{db}"
            else:
                #check for version 7.4.2 and set download_url 
                download_url = "https://" + fqdn + ":9443/v1/debuginfo/all"
                #download_url = "https://" + fqdn + ":9443/v1/bdbs/debuginfo"   7.4.2 or higher
            
            logger.info(f"({fqdn}):Starting Download")        
            response = requests.get(download_url, auth=(username, password), verify=False)
            response.raise_for_status()
            fname = SupportPackage.get_fname(fqdn,path) 

            if (reduce_tar_size):
                logger.info(f"({fqdn}):Reducing Package Size")
                tar_processor_bytes = TarProcessor()
                savings, original_size, new_size, new_tar_bytes = tar_processor_bytes.process_from_bytes(response.content)

                logger.info(f"({fqdn}):Original tar size: {original_size} bytes")
                logger.info(f"({fqdn}):New tar size: {new_size} bytes")
                logger.info(f"({fqdn}):Storage savings: {savings} bytes")

                with open(fname, "wb") as f:
                    f.write(new_tar_bytes)
            else:
                with open(fname, "wb") as f:
                    f.write(response.content)

            logger.info(f"({fqdn}):Support package downloaded successfully.")
        except requests.exceptions.RequestException as e:
            logger.exception(e,f"({fqdn}):Error downloading support package")
