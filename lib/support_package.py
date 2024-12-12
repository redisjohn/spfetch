"""redis api module"""
import os
import json
from datetime import datetime
import requests
from .tar_processor import TarProcessor
from .logger import Logger
from .files_uploader import FilesUploader


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
    def summarize_node_info(response):
        """summarize node info"""
        node_info = {}
        version_mismatch = False
        os_mismatch = False
        node_count = 0
        version = ''
        os_version = ''
        nodes_json = json.loads(response)
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
    def get_nodes(logger, fqdn, ip, username, password):
        """Get cluster node info"""
        try:
            requests.packages.urllib3.disable_warnings()
            host = fqdn if (ip is None) else ip
            download_url = "https://" + host + ":9443/v1/nodes"
            response = requests.get(
                download_url,
                auth=(
                    username,
                    password),
                verify=False,
                timeout=500)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logger.exception(e, f"Error Getting Node Information{fqdn}")

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
            if (bdb['slave_ha']):
                bdb['shards_count'] *= 2
            print(f"{str(bdb['uid']).ljust(uid_width)}  {str(bdb['name']).ljust(name_width)} {str(bdb['version']).ljust(version_width)} {str(bdb['shards_count']).rjust(shards_width)}")

    def deserialize_bdb_info(fqdn, response):
        """deseriazie bdb info"""
        bdbs = []
        bdb_json = sorted(json.loads(response), key=lambda x: (x['uid']))

        for bdb in bdb_json:

            rec = {}
            rec['Id'] = bdb['uid']
            rec['Name'] = bdb['name']
            rec['Version'] = bdb['version']
            rec['Total Shards'] = bdb['shards_count'] if not bdb['slave_ha'] else bdb['shards_count'] * 2
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
                rec['modules'] += (module + ' ')
            rec['TLS'] = bdb['ssl']
            rec['OSS Cluster API'] = bdb['oss_cluster']
            rec['Proxy Policy'] = bdb['proxy_policy']
            rec['Shard Placement'] = bdb['shards_placement']

            bdbs.append(rec)

        return bdbs

    @staticmethod
    def get_bdb_names(logger, fqdn, ip, username, password):
        """get bdb names"""
        response = None
        try:
            requests.packages.urllib3.disable_warnings()
            host = fqdn if (ip is None) else ip
            download_url = "https://" + host + ":9443/v1/bdbs"
            response = requests.get(
                download_url,
                auth=(
                    username,
                    password),
                verify=False,
                timeout=500)
            response.raise_for_status()
            return response.text
        except requests.exceptions.ConnectionError as e:
            logger.exception(e, f"({fqdn}):Connection Error Occured")
        except requests.exceptions.HTTPError as e:
            if (response.status_code == 401):
                logger.exception(
                    e, f"({fqdn}):{response.status_code}:Invalid Credentials")
            else:
                logger.exception(e, f"({fqdn}):HTTP Error")

    @staticmethod
    def deserialize_license_info(fqdn, response):
        """license info"""
        redis_license = json.loads(response)
        output = {}
        output['cluster'] = fqdn
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
        try:
            requests.packages.urllib3.disable_warnings()
            host = fqdn if (ip is None) else ip
            download_url = "https://" + host + ":9443/v1/license"
            response = requests.get(
                download_url,
                auth=(
                    username,
                    password),
                verify=False,
                timeout=500)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error License Info for {fqdn}: {e}")

    @staticmethod
    def download_package(logger, fqdn, ip, username, password, path, db,
                         reduce_tar_size, save_to_file=True, upload=True, dry_run=False):
        """Download suppport package"""
        try:
            output_bytes = []
            requests.packages.urllib3.disable_warnings()
            host = fqdn if (ip is None) else ip
            if db != 0:
                logger.info(f"Database:{db}")
                download_url = "https://" + host + \
                    f":9443/v1/debuginfo/node/bdb/{db}"
            else:
                # check for version 7.4.2 and set download_url
                download_url = "https://" + host + ":9443/v1/debuginfo/all"
                # download_url = "https://" + host + ":9443/v1/bdbs/debuginfo"
                # 7.4.2 or higher

            logger.info(f"({fqdn}):Starting Download")
            if not dry_run:
                response = requests.get(
                    download_url,
                    auth=(
                        username,
                        password),
                    verify=False,
                    timeout=500)
                response.raise_for_status()
            else:
                logger.info("Dryrun Only")

            fname = SupportPackage.get_fname(fqdn, path)

            if reduce_tar_size:
                logger.info(f"({fqdn}):Reducing Package Size")
                if not dry_run:
                    tar_processor_bytes = TarProcessor()
                    savings, original_size, new_size, output_bytes = tar_processor_bytes.process_from_bytes(response.content)
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
