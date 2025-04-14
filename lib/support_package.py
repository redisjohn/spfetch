"""redis api module"""
import os
import json
from datetime import datetime
import requests
from .tar_processor import TarProcessor
from .files_uploader import FilesUploader
from .certificate_inspector import CertificateInspector


class SupportPackage:
    """Redis API Class"""
    @staticmethod
    def convert_zulu_string(date_string):
        """convert Zulu String"""
        date_object = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
        formatted_date = date_object.strftime("%Y-%m-%d")
        return formatted_date

    @staticmethod
    def get_fname(fqdn, path):
        """format file name"""
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y%m%d%H%M%S")
        fname = f"debuginfo.{fqdn}_{formatted_time}.tar.gz"
        if not os.path.exists(path):
            os.makedirs(path)
        return os.path.join(path, fname)

    @staticmethod
    def api_request(fqdn, ip, username, password,api_path):     
        response = None  
        host = fqdn if (ip is None) else ip
        url = "https://" + host + ":9443" + api_path
        try:
            requests.packages.urllib3.disable_warnings()
            response = requests.get(
                url,
                auth=(
                    username,
                    password),
                verify=False,
                timeout=500)
            response.raise_for_status()          
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error:{response.status_code}:{fqdn}:{url}:{e}")
        except requests.exceptions.HTTPError as e:
                print(f"Error:{response.status_code}:{fqdn}:{url}:Invalid Credentials")

    @staticmethod
    def get_authenciation_scheme(bdb):
        if (bdb["authentication_redis_pass"]):
            return "Default User With Password"
        elif (bdb["roles_permissions"]):
            return "Using ACLS"
        else:
            return "Default User No Password"

    @staticmethod
    def summarize_node_info(fqdn, ip, username, password):
        """summarize node info"""
        response = SupportPackage.api_request(fqdn,ip,username,password,"/v1/nodes")
        node_info = {}
        version_mismatch = False
        os_mismatch = False
        node_count = 0
        version = ''
        os_version = ''
        
        nodes_json = json.loads(response.text)
        for node in nodes_json:
            if node_count == 0:
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
        node_info['mismatch'] = True if (
            os_mismatch | version_mismatch) else False
        return node_info

    @staticmethod
    def get_nodes(fqdn,ip,username,password):
        response = SupportPackage.api_request(fqdn,ip,username,password,"/v1/nodes")        
        data = json.loads(response.text)        
        nodes = []
        
        for item in data:
            node={}
            #"accept_servers": true,
            node["fqdn"] = fqdn
            node["id"] = item["uid"]
            node["status"] = item["status"]
            node["addr"] = item["addr"]
            node["rack_id"] = item["rack_id"] 
            node["os_version"] = item["os_version"] 
            node["architecture"] = item["architecture"]
            node["cores"]= item["cores"]
            node["software_version"] = item["software_version"]
            node["shard_count"] = item["shard_count"]
            node["shard_list"] = ''
            for shard in item["shard_list"]:
                node["shard_list"] += str(shard) + ','
            node["shard_list"] =  node["shard_list"][:-1]        
            node["memory GiB"] = round((item["total_memory"]/(1024**3)),2)
            nodes.append(node)

        return nodes

    @staticmethod
    def tablulate_bdb_info(fqdn, response):
        """tabulate bdb info"""
        bdb_json = json.loads(response)

        # sort by uid
        bdb_names = sorted(bdb_json, key=lambda x: x['uid'])

        # column width for tablular format
        name_width = max(len(bdb['name']) for bdb in bdb_names) + 2
        uid_width = max(len(str(bdb['uid'])) for bdb in bdb_names) + 2
        version_width = max(len(str(bdb['version'])) for bdb in bdb_names) + 2
        shards_width = max(len(str(bdb['shards_count']))
                           for bdb in bdb_names) + 2

        print('\n' + fqdn)
        print(f"{'Id'.ljust(uid_width)} {'Name'.ljust(name_width)} {'Version'.ljust(version_width)} {'Shards'.ljust(shards_width)}")
        print('-' * (uid_width + name_width + version_width + shards_width + 6))

        for bdb in bdb_names:
            if bdb['slave_ha']:
                bdb['shards_count'] *= 2
            print(f"{str(bdb['uid']).ljust(uid_width)}  {str(bdb['name']).ljust(name_width)} {str(bdb['version']).ljust(version_width)} {str(bdb['shards_count']).rjust(shards_width)}")

    @staticmethod
    def deserialize_bdb_info(fqdn,response):
        """deserialize bdb info"""
        bdbs = []
        bdb_json = sorted(json.loads(response), key=lambda x: (x['uid']))

        for bdb in bdb_json:
            rec = {}
            rec['fqdn'] = fqdn
            rec['Id'] = bdb['uid']
            rec['Name'] = bdb['name']
            rec['Version'] = bdb['version']
            rec['Total Shards'] = bdb['shards_count'] if not bdb['slave_ha'] else bdb['shards_count'] * 2
            rec['Memory GiB']=round((bdb['memory_size']/ (1024 ** 3)),2)
            rec['High Availability'] = bdb['slave_ha']
            rec['Flex'] = bdb['bigstore']
            rec['Created'] = SupportPackage.convert_zulu_string(
                bdb['created_time'])
            rec['Modified'] = SupportPackage.convert_zulu_string(
                bdb['last_changed_time'])
            rec['Persistence'] = bdb['data_persistence']
            rec['Eviction Policy'] = bdb['eviction_policy']
            rec['CRDB'] = bdb['crdt']
            rec['Modules'] = ''
            for module in bdb['module_list']:
                # print(module)
                rec['Modules'] += module['module_name'] + \
                    ' ' + module['semantic_version'] + ';'
            rec['Modules'] = rec['Modules'][:-1]  
            rec['TLS'] = bdb['tls_mode']       
            rec['Authentication'] = SupportPackage.get_authenciation_scheme(bdb)
            rec['OSS Cluster API'] = bdb['oss_cluster']
            rec['Proxy Policy'] = bdb['proxy_policy']
            rec['Shard Placement'] = bdb['shards_placement']
            endpoints = bdb['endpoints']            
            for endpoint in endpoints:                
                nameport = endpoint['dns_name'] + ":" + str(endpoint['port'])
                if endpoint['addr_type'] == "external":
                    rec['External Endpoint'] = nameport
                else:
                    rec['Internal Endpoint'] = nameport
            bdbs.append(rec)
        return bdbs

    @staticmethod
    def get_bdb_names(fqdn, ip, username, password):
        """get bdb names"""
        response = SupportPackage.api_request(fqdn,ip,username,password,"/v1/bdbs")
        return response.text
    
    @staticmethod
    def deserialize_license_info(fqdn, response):
        """license info"""
        redis_license = json.loads(response)
        output = {}
        output['cluster'] = fqdn
        output['cluster_name'] = redis_license['cluster_name']
        output['owner'] = redis_license['owner']
        output['expired'] = redis_license['expired']
        output['expiration'] = SupportPackage.convert_zulu_string(
            redis_license['expiration_date'])
        output['shards_limit'] = redis_license['shards_limit']
        output['ram_shards'] = redis_license['ram_shards_in_use']
        output['flash_shards'] = redis_license['flash_shards_in_use']
        return output

    @staticmethod
    def get_license_info(fqdn, ip, username, password):
        """get redis license info"""
        response =  SupportPackage.api_request(fqdn,ip,username,password,"/v1/license")
        return response.text

    @staticmethod
    def download_package(logger, fqdn, ip, username, password, path, db,
                         reduce_tar_size, save_to_file=True, upload=True, dry_run=False):
        """Download suppport package"""
        try:
            output_bytes = []
            host = fqdn if (ip is None) else ip
            if db != 0:
                logger.info(f"Database:{db}")
                apipath = f"/v1/debuginfo/node/bdb/{db}" 
            else:
                apipath = "/v1/debuginfo/all"
                # 7.4.2 or higher
                # use /v1/bdbs/debuginfo

            logger.info(f"({fqdn}):Starting Download")
            if not dry_run:
                response = SupportPackage.api_request(fqdn,ip,username,password,apipath)                
            else:
                logger.info("Dryrun Only")

            fname = SupportPackage.get_fname(fqdn, path)

            if reduce_tar_size:
                logger.info(f"({fqdn}):Reducing Package Size")
                if not dry_run:
                    tar_processor_bytes = TarProcessor()
                    savings, original_size, new_size, output_bytes = tar_processor_bytes.process_from_bytes(
                        response.content)
                    logger.info(
                        f"({fqdn}):Original tar size: {original_size}MB")
                    logger.info(f"({fqdn}):New tar size: {new_size}MB")
                    logger.info(f"({fqdn}):Storage savings: {savings}MB")
            else:
                if not dry_run:
                    output_bytes = response.content

            if save_to_file:
                if not dry_run:
                    with open(fname, "wb") as f:
                        f.write(output_bytes)
                logger.info(
                    f"({fqdn}):Support Package Downloaded and Saved:({fname})")

            if upload:
                if not reduce_tar_size:
                    logger.info(
                        f"{fqdn}:Uploading Bloated Support Packages Not Supported")
                else:
                    logger.info(f"({fqdn}):Uploading to redis.io")
                    if not dry_run:
                        try:
                            FilesUploader.upload_bytes(output_bytes, fname)
                            # FilesUploader.upload_file(fname)
                            logger.info(
                                f"({fqdn}):Support package uploaded successfully.")
                        except Exception as e:
                            logger.exception(e, "Error During Upload")

        except requests.exceptions.RequestException as e:
            logger.exception(e, f"({fqdn}):Error downloading support package")

    @staticmethod
    def deserialize_certificates(fqdn,serialized_json):
        outputs = []
        redis_certs = json.loads(serialized_json)
        for certname, pem in redis_certs.items():
            if 'cert' in certname:                            
                inspector = CertificateInspector(pem)
                output = {}
                output["fqdn"] = fqdn
                output["source"] = "cluster"                
                output["cert"] = certname
                output["expiration"] = inspector.get_expiration_date().strftime("%Y-%m-%d %H:%M:%S")
                output["subject"] = str(inspector.get_subject())
                output["issuer"] = str(inspector.get_issuer())
                outputs.append(output)
        return outputs    

    @staticmethod
    def get_bdb_certs(fqdn,ip,username,password):
        response = SupportPackage.api_request(fqdn,ip,username,password,"/v1/bdbs")
        bdbs = json.loads(response.text)
        bdb_certs = []
        for bdb in bdbs:
            for cert in bdb["authentication_ssl_client_certs"]:
                bdb_cert = {}
                inspector = CertificateInspector(cert["client_cert"])
                bdb_cert["fqdn"] = fqdn
                bdb_cert["source"] = f"{bdb['name']} ({bdb['uid']})" 
                bdb_cert["cert"] = "client cert"                
                bdb_cert["expiration"] = inspector.get_expiration_date().strftime("%Y-%m-%d %H:%M:%S")
                bdb_cert["subject"] = str(inspector.get_subject())
                bdb_cert["issuer"] = str(inspector.get_issuer())
                bdb_certs.append(bdb_cert)
        return bdb_certs        

    @staticmethod
    def get_certificate_info(fqdn, ip, username, password):
        certificates = []
        response = SupportPackage.api_request(fqdn,ip,username,password,"/v1/cluster/certificates")
        certs = SupportPackage.deserialize_certificates(fqdn,response.text)
        for cert in certs:
            certificates.append(cert)        
        bdb_certs = SupportPackage.get_bdb_certs(fqdn,ip,username,password)
        certificates.extend(bdb_certs)

        return sorted(certificates, key=lambda x:(x['fqdn'], x['source'], x['cert']))
   
    @staticmethod
    def get_roles_acls(fqdn, ip, username, password):
        response = SupportPackage.api_request(fqdn,ip,username,password,"/v1/roles")        
        data = json.loads(response.text)
        
        roles = []
        
        for item in data:
            role = {}
            role["fqdn"]=fqdn
            role["uid"]=item["uid"]
            role["name"] =item["name"]
            role["management"]=item["management"]
            roles.append(role)

        response = SupportPackage.api_request(fqdn,ip,username,password,"/v1/redis_acls")
        data = json.loads(response.text)
        acls = []
        for item in data:
            acl = {}
            acl["fqdn"]=fqdn
            acl["uid"]=item["uid"]
            acl["name"]=item["name"]
            acl["acl"]=item["acl"]
            acls.append(acl)

        response = SupportPackage.api_request(fqdn,ip,username,password,"/v1/bdbs")
        data = json.loads(response.text)
        roles_permissions = []
        for bdb in data:
            rules = bdb["roles_permissions"]
            for rule in rules:
                role_permission = {}
                role_permission["fqdn"]=fqdn
                role_permission["Id"]=bdb["uid"]
                role_permission["Name"]=bdb["name"]
                role_permission["Order"]=rule["order"]
                role_permission["Role"]=next((i["name"] for i in roles if i["uid"]==rule["role_uid"]))
                role_permission["Acl"]=next((i["name"] for i in acls if i["uid"]==rule["redis_acl_uid"]))
                roles_permissions.append(role_permission)

        #holding off on users because of RE permissions required (Admin)
        #users = SupportPackage.api_request(fqdn,ip,username,password,"/v1/users")

        return sorted(roles, key=lambda x:x["uid"]), sorted(acls, key=lambda x:x["uid"]), roles_permissions  