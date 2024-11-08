#!/usr/bin/python3
import argparse
from SupportPackage import SupportPackage
from CredentialVault import CredentialVault
from ExcelReportGenerator import ExcelReportGenerator
from Logger import Logger
from Fqdns import FQDNs
from datetime import datetime
import os
import re
import json

def sort_and_keep_latest_files(logger,folder_path, file_prefix, n):
    # Get a list of all files in the folder
    all_files = os.listdir(folder_path)

    # Filter files that match the prefix
    matched_files = [file for file in all_files if re.match(f'^{file_prefix}.*', file)]

    # Sort matched files by creation time
    sorted_files = sorted(matched_files, key=lambda x: os.path.getctime(os.path.join(folder_path, x)))

    # Keep only the last n files
    files_to_keep = sorted_files[-n:]

    # Delete files that match the prefix but are not in files_to_keep list
    for file in matched_files:
        if file not in files_to_keep:
            fname = os.path.join(folder_path, file)
            logger.info(f"Purging Old Version:({fname})")
            os.remove(fname)

def get_fname(path):
            current_time = datetime.now()
            formatted_time = current_time.strftime("%Y%m%d%H%M%S")            
            fname = f"inventory_{formatted_time}.xlsx"
            if not os.path.exists(path):
                os.makedirs(path)
            return os.path.join(path,fname)

def xls(logger,fqdns,path):
    clusters = []

    # Create a new instance of the generator
    generator = ExcelReportGenerator()

    # Create a new workbook and add data
    generator.CreateWorkbook()
    generator.CreateSheet("Clusters")

    for fqdn in fqdns:
        try:
            user,pwd = CredentialVault.decrypt_credentials(fqdn)

            # get license and node info for cluster sheet
            logger.info(f"Processing Data for:({fqdn})")

            response = SupportPackage.get_license_info(fqdn,user,pwd)
            #license = SupportPackage.deserialize_license_info(fqdn,response)
            license = json.loads(response)

            response = SupportPackage.get_nodes(logger,fqdn,user,pwd)
            nodeinfo = SupportPackage.summarize_node_info(response)
            
            cluster = {}
            cluster['name'] = fqdn
            cluster['version'] = nodeinfo['version']
            cluster['os'] = nodeinfo['os']

            cluster['features'] = ''
            for feature in license['features']:
                cluster['features'] += (feature + ' ')
            clusters.append(cluster)

            cluster['activated'] = SupportPackage.convert_zulu_string(license['activation_date'])
            cluster['expiration'] = SupportPackage.convert_zulu_string(license['expiration_date'])
            cluster['expired'] = license['expired']
            cluster['shard_limit'] = license['shards_limit']
            cluster['ram_shards'] = license['ram_shards_in_use']
            cluster['rof_shards'] = license['flash_shards_in_use']
            cluster['nodes'] = nodeinfo['nodes']
            cluster['version_mismatch'] = nodeinfo['mismatch']
 
            # create sheet for fqdn 
            response = SupportPackage.get_bdb_names(logger,fqdn,user,pwd)
            bdb_data = SupportPackage.deserialize_bdb_info(fqdn,response)            
            generator.CreateSheet(fqdn)
            generator.AddData(fqdn,bdb_data)
        except Exception as e:
            logger.exception(e,f"Error during Request for {fqdn}")

        
    # add licenses to cluster worksheet        
    generator.AddData("Clusters",clusters)     
    #save the workbook   
    file_name = generator.SaveWorkbook(get_fname(path))   
    logger.info(f"Workbook saved as '{file_name}'.")

def process(logger,fqdn,user,pwd,path,args):

    if (args.list):
        try: 
            response = SupportPackage.get_bdb_names(logger,fqdn,user,pwd)
            if (args.json):
                bdb_info = SupportPackage.deserialize_bdb_info(fqdn,response)
                bdb = {}
                bdb['cluster'] = fqdn
                bdb['databases'] = bdb_info
                print(json.dumps(bdb, indent=4))
            else:
                SupportPackage.tablulate_bdb_info(fqdn,response)
        except Exception as e:
            logger.exception(e,f"Error Processing Command")
    elif (args.license):
        response = SupportPackage.get_license_info(fqdn,user,pwd)
        license = SupportPackage.deserialize_license_info(fqdn,response)
        print(json.dumps(license, indent=4)) 
    else:
        try: 
            if args.bloat:
                reduce_tar_size = False                 
            else:
                logger.info(f"({fqdn}):Agressively Optimizing Support Package Size")
                reduce_tar_size = True

            save_to_file = True

            if (args.nosave):
                if args.upload:
                    logger.info(f"({fqdn}):Support Package will not be saved to disk")
                    save_to_file = False

            db = 0 if (args.db is None) else args.db

            SupportPackage.download_package(logger,fqdn, user,pwd,path,db,reduce_tar_size,save_to_file=save_to_file,upload=args.upload,dry_run=args.dryrun) 
        
            keep = int(args.keep) if (args.keep is not None) else 1

            sort_and_keep_latest_files(logger,path,f'debuginfo.{fqdn}',keep)    
        
        except Exception as e:
            logger.exception(e,f"({fqdn}):Fatal Error")
    return

#
# Process command arguments for specified fqdn
#
def process_args_single_fqdn(logger,fqdn,args,path):
        user = ''
        pwd = ''

        if (args.user is not None):
            user = args.user
            if (args.pwd is None):
                logger.error(f"({fqdn}):Missing Password")
                exit(-1)
            else:
                pwd = args.pwd
        else:
            try:
                user,pwd = CredentialVault.decrypt_credentials(fqdn)
            except Exception as e:
                logger.exception(e,f"Fatal Error")
                exit(-1)
        try:
            process(logger,fqdn,user,pwd,path,args)
        except Exception as e:
            logger.exception(e,f"Fatal Error")
            exit(-1)

def main():
    parser = argparse.ArgumentParser(description="Redis Enterprise Audit Tool Version 0.9")

    parser.add_argument("fqdn", help="Fully Qualified Domain Name of Cluster (wildcards supported if credentials in vault))") 
    parser.add_argument("--user", help="Username for authentication")
    parser.add_argument("--pwd", help="Password for Authentication")
    parser.add_argument("--path", help="Folder path for saving Output Files")
    parser.add_argument("--db", help="Database Id")
    parser.add_argument("--upload",action='store_true',help="Upload Package to Redis.io (requires API KEY)")
    parser.add_argument("--nosave", action='store_true',help="Do not save support package to disk (works only with --upload")
    parser.add_argument("--keep",help="Number of Output files to keep")
    parser.add_argument("--bloat",action='store_true',help="Make no attempt to reduce the Package Size") 
    parser.add_argument("--dryrun",action='store_true',help="Do a dryrun for testing") 
    parser.add_argument("--list",action='store_true',help="List Databases Id and Names")
    parser.add_argument("--json",action='store_true',help="Format database output list in Json")
    parser.add_argument("--license",action='store_true',help="List Databases Id and Names")
    parser.add_argument("--xls",action='store_true',help="Generate Excel Inventory Report For All Clusters")
    
    logger = Logger(name='MyLogger', facility='spfetch', log_to_file=False, filename='logs/app')

    args = parser.parse_args()
   

    if args.path:
        path = args.path
    else:
        path = "output"   
    
    fqdn = args.fqdn if args.fqdn != '.' else '*'

    fqdns = FQDNs.get(fqdn)

    #  user pwd parameters override if found in vault 
    # also do not allow if user/pwd parameters supplied with wildcard fqdn like (*.redis.test) 
    if (args.user is not None):
        if len(fqdns) < 2 :
            if (len(fqdns) == 1):
                if (fqdns[0] != fqdn):
                    logger.error(f"fqdn {fqdn} is not compatible with --user")                    
                    return
            process_args_single_fqdn(logger,fqdn,args,path)
    elif (len(fqdns) == 0):
        logger.error("no matches found")
    else:
        if not args.xls:
            for fqdn in fqdns:
                try:
                    user,pwd = CredentialVault.decrypt_credentials(fqdn)
                    process(logger,fqdn,user,pwd,path,args) 
                except Exception as e:
                    logger.exception(e,f"({fqdn}):Error during Request")
        else:
            xls(logger,fqdns,path)
            keep = int(args.keep) if (args.keep is not None) else 5
            sort_and_keep_latest_files(logger,path,"inventory",keep)    
    
if __name__ == "__main__":

     main()

