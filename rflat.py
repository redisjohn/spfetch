#!/usr/bin/env python3
import argparse
from datetime import datetime
import os
import re
import json
import sys
from lib.support_package import SupportPackage
from lib.credential_vault import CredentialVault
from lib.excel_report_generator import ExcelReportGenerator
from lib.logger import Logger
from lib.fqdns import FQDNs
from lib.resolver import Resolver

def sort_and_keep_latest_files(logger, folder_path, file_prefix, n):
    """expunge old files"""
    # Get a list of all files in the folder
    all_files = os.listdir(folder_path)

    # Filter files that match the prefix
    matched_files = [file for file in all_files if re.match(f"^{file_prefix}.*", file)]

    # Sort matched files by creation time
    sorted_files = sorted(
        matched_files, key=lambda x: os.path.getctime(os.path.join(folder_path, x))
    )

    # Keep only the last n files
    files_to_keep = sorted_files[-n:]

    # Delete files that match the prefix but are not in files_to_keep list
    for file in matched_files:
        if file not in files_to_keep:
            fname = os.path.join(folder_path, file)
            logger.info(f"Purging Old Version:({fname})")
            os.remove(fname)


def get_fname(path):
    """format filename from timestamp"""
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y%m%d%H%M%S")
    fname = f"inventory_{formatted_time}.xlsx"
    if not os.path.exists(path):
        os.makedirs(path)
    return os.path.join(path, fname)


def xls(logger, fqdns, resolver, path):
    """Generate xls file for inventory"""
    clusters = []
    certificates = []
    roles = []
    acls = []
    permissions = []
    nodes = []
    databases = []
    ciphers = []
    shards = []

    # Create a new instance of the generator
    generator = ExcelReportGenerator()

    # Create a new workbook and add data
    generator.create_workbook()
    generator.create_sheet("Clusters",tab_color="55585c")
    generator.create_sheet("Nodes",tab_color="55585c")
    generator.create_sheet("Shards",tab_color="55585c")

    generator.create_sheet("Certificates",tab_color="591523")
    generator.create_sheet("Roles",tab_color="591523")
    generator.create_sheet("Acls",tab_color="591523")
    generator.create_sheet("Permissions",tab_color="591523")
    generator.create_sheet("Ciphers",tab_color="591523")

    generator.create_sheet("Databases",tab_color="154859")
    for fqdn in fqdns:
        try:
            user, pwd = CredentialVault.decrypt_credentials(fqdn)
            ip = resolver.get(fqdn)
            # get license and node info for cluster sheet
            logger.info(f"Processing Data for:({fqdn})")

            response = SupportPackage.get_license_info(fqdn,ip, user, pwd)
            redis_license = json.loads(response)

            cluster_data = SupportPackage.get_cluster_info(fqdn,ip, user,pwd)
            cluster_json = json.loads(cluster_data)
            
            bdb_data = SupportPackage.get_bdbs(fqdn,ip,user,pwd)
            bdb_json = json.loads(bdb_data)

            fqdn_roles, fqdn_acls, fqdn_permissions = SupportPackage.get_roles_acls(bdb_json,fqdn,ip,user,pwd)
            roles.extend(fqdn_roles)
            acls.extend(fqdn_acls)
            permissions.extend(fqdn_permissions)
        
            fqdn_certificates = SupportPackage.get_certificate_info(fqdn,bdb_json,cluster_json)
            certificates.extend(fqdn_certificates)

            nodeinfo = SupportPackage.summarize_node_info(fqdn,ip, user, pwd)

            cluster = {}
            cluster["fqdn"] = fqdn
            cluster["cluster_name"] = redis_license['cluster_name']
            cluster["license_owner"] = redis_license['owner']
            cluster["version"] = nodeinfo["version"]
            cluster["os"] = nodeinfo["os"]
            cluster["rack aware"]=cluster_json["rack_aware"]
            cluster["features"] = ""
            for feature in redis_license["features"]:
                cluster["features"] += feature + " "

            cluster["activated"] = SupportPackage.convert_zulu_string(
                redis_license["activation_date"]
            )
            cluster["expiration"] = SupportPackage.convert_zulu_string(
                redis_license["expiration_date"]
            )
            cluster["expired"] = redis_license["expired"]
            cluster["shard_limit"] = redis_license["shards_limit"]
            cluster["ram_shards"] = redis_license["ram_shards_in_use"]
            cluster["rof_shards"] = redis_license["flash_shards_in_use"]
            cluster["nodes"] = nodeinfo["nodes"]
            cluster["version_mismatch"] = nodeinfo["mismatch"]
            clusters.append(cluster)

            fqdn_nodes = SupportPackage.get_nodes(fqdn,ip,user,pwd)
            nodes.extend(fqdn_nodes)   

            fqdn_shards = SupportPackage.get_shard_info(bdb_json,fqdn,ip,user,pwd)            
            shards.extend(fqdn_shards)

            bdb_data = SupportPackage.deserialize_bdb_info(fqdn,bdb_json)
            databases.extend(bdb_data)
            
            fqdn_ciphers = SupportPackage.get_ciphers(fqdn,cluster_json)            
            ciphers.extend(fqdn_ciphers)

    
        except Exception as e:
            logger.exception(e, f"Error during Request for {fqdn}")

    # add licenses to cluster worksheet
    generator.add_data("Clusters", clusters)
    generator.add_data("Nodes", nodes)
    generator.add_data("Shards",shards)
    generator.add_data("Certificates",certificates)
    generator.add_data("Ciphers",ciphers)
    generator.add_data("Roles",roles)
    generator.add_data("Acls",acls)
    generator.add_data("Permissions",permissions)
    generator.add_data("Databases",databases)
    
    # save the workbook
    file_name = generator.save_workbook(get_fname(path))
    logger.info(f"Workbook saved as '{file_name}'.")

def process(logger, fqdn, ip, user, pwd, path, args):
    '''process a command'''
    if args.list:
        try:
            bdb_data = SupportPackage.get_bdbs(fqdn, ip, user, pwd)
            bdb_json = json.loads(bdb_data)
            if args.json:
                bdb_info = SupportPackage.deserialize_bdb_info(fqdn,bdb_json)
                bdb = {}
                bdb["cluster"] = fqdn
                bdb["databases"] = bdb_info
                print(json.dumps(bdb, indent=4))
            else:
                SupportPackage.tablulate_bdb_info(fqdn, bdb_json)
        except Exception as e:
            logger.exception(e, f"{fqdn}-Error Processing Command")
    elif args.license:
        response = SupportPackage.get_license_info(fqdn, ip, user, pwd)
        redis_license = SupportPackage.deserialize_license_info(fqdn, response)
        print(json.dumps(redis_license, indent=4))
    else:
        try:
            if args.bloat:
                reduce_tar_size = False
            else:
                logger.info(f"({fqdn}):Agressively Optimizing Support Package Size")
                reduce_tar_size = True

            save_to_file = True

            if args.nosave:
                if args.upload:
                    logger.info(f"({fqdn}):Support Package will not be saved to disk")
                    save_to_file = False

            db = 0 if (args.db is None) else args.db

            SupportPackage.download_package(
                logger,
                fqdn,
                ip,
                user,
                pwd,
                path,
                db,
                reduce_tar_size,
                save_to_file=save_to_file,
                upload=args.upload,
                dry_run=args.dryrun,
            )

            keep = int(args.keep) if (args.keep is not None) else 1

            sort_and_keep_latest_files(logger, path, f"debuginfo.{fqdn}", keep)

        except Exception as e:
            logger.exception(e, f"({fqdn}):Fatal Error")
    return

#
# Process command arguments for specified fqdn
#

def process_args_single_fqdn(logger, fqdn, ip, args, path):
    '''process command for single fqdn'''
    user = ""
    pwd = ""

    if args.user is not None:
        user = args.user
        if args.pwd is None:
            logger.error(f"({fqdn}):Missing Password")
            sys.exit(-1)
        else:
            pwd = args.pwd
    else:
        try:
            user, pwd = CredentialVault.decrypt_credentials(fqdn)
        except Exception as e:
            logger.exception(e, "Fatal Error")
            sys.exit(-1)
    try:
        process(logger, fqdn, ip, user, pwd, path, args)
    except Exception as e:
        logger.exception(e,"Fatal Error")
        sys.exit(-1)


def main():
    '''main function'''

    parser = argparse.ArgumentParser(
        description="Redis Enterprise Audit Tool Version 250415"
    )

    parser.add_argument(
        "fqdn",
        help="Fully Qualified Domain Name of Cluster (wildcards supported)",
    )
    parser.add_argument("--user", help="Username for authentication")
    parser.add_argument("--pwd", help="Password for Authentication")
    parser.add_argument("--path", help="Folder path for saving Output Files")
    parser.add_argument("--db", help="Database Id")
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Upload Package to Redis.io (requires API KEY)",
    )
    parser.add_argument(
        "--nosave",
        action="store_true",
        help="Do not save support package to disk (works only with --upload",
    )
    parser.add_argument("--keep", help="Number of Output files to keep")
    parser.add_argument(
        "--bloat",
        action="store_true",
        help="Make no attempt to reduce the Package Size",
    )
    parser.add_argument("--dryrun", action="store_true", help="Do a dryrun for testing")
    parser.add_argument(
        "--list", action="store_true", help="List Databases Id and Names"
    )
    parser.add_argument(
        "--json", action="store_true", help="Format database output list in Json"
    )
    parser.add_argument(
        "--license", action="store_true", help="List Databases Id and Names"
    )
    parser.add_argument(
        "--xls",
        action="store_true",
        help="Generate Excel Inventory Report For All Clusters",
    )

    logger = Logger(
        name="MyLogger", facility="rflat", log_to_file=False, filename="logs/app"
    )

    resolver = Resolver()
    resolver.load()

    args = parser.parse_args()

    if args.path:
        path = args.path
    else:
        path = "output"

    fqdn = args.fqdn if args.fqdn != "." else "*"

    fqdns = FQDNs.get(fqdn)

    #  user pwd parameters override if found in vault
    # also do not allow if user/pwd parameters supplied with wildcard fqdn
    # like (*.redis.test)
    if args.user is not None:
        if len(fqdns) < 2:
            if len(fqdns) == 1:
                if fqdns[0] != fqdn:
                    logger.error(f"fqdn {fqdn} is not compatible with --user")
                    return
            process_args_single_fqdn(logger, fqdn, resolver.get(fqdn), args, path)
    elif len(fqdns) == 0:
        logger.error("no matches found")
    else:
        if not args.xls:
            for fqdn in fqdns:
                try:
                    user, pwd = CredentialVault.decrypt_credentials(fqdn)
                    process(logger, fqdn, resolver.get(fqdn), user, pwd, path, args)
                except Exception as e:
                    logger.exception(e, f"({fqdn}):Error during Request")
        else:
            xls(logger, fqdns, resolver, path)
            keep = int(args.keep) if (args.keep is not None) else 5
            sort_and_keep_latest_files(logger, path, "inventory", keep)


if __name__ == "__main__":

    main()
