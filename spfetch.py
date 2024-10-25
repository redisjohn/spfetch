
import argparse
from SupportPackage import SupportPackage
from CredentialVault import CredentialVault
from ExcelReportGenerator import ExcelReportGenerator
from Fqdns import FQDNs
from datetime import datetime
import os
import re
import json



def sort_and_keep_latest_files(folder_path, file_prefix, n):
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
            print(f"Purging Old Version:({fname}")
            os.remove(fname)

def get_fname(path):
            current_time = datetime.now()
            formatted_time = current_time.strftime("%Y%m%d%H%M%S")            
            fname = f"inventory_{formatted_time}.xlsx"
            if not os.path.exists(path):
                os.makedirs(path)
            return os.path.join(path,fname)

def xls(path):
    clusters = []
    fqdns = FQDNs.get()

 # Create a new instance of the generator
    generator = ExcelReportGenerator()

    # Create a new workbook and add data
    generator.CreateWorkbook()
    generator.CreateSheet("Clusters")

    for fqdn in fqdns:
        try:
            user,pwd = CredentialVault.decrypt_credentials(fqdn)

            # get license and node info for cluster sheet
            print(f"Processing Data for:({fqdn})")

            response = SupportPackage.get_license_info(fqdn,user,pwd)
            #license = SupportPackage.deserialize_license_info(fqdn,response)
            license = json.loads(response)

            response = SupportPackage.get_nodes(fqdn,user,pwd)
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
            response = SupportPackage.get_bdb_names(fqdn,user,pwd)
            bdb_data = SupportPackage.deserialize_bdb_info(fqdn,response)            
            generator.CreateSheet(fqdn)
            generator.AddData(fqdn,bdb_data)
        except Exception as e:
            print(f"Error during Request for {fqdn}:{e}")

        
    # add licenses to cluster worksheet        
    generator.AddData("Clusters",clusters)     
    #save the workbook   
    generator.SaveWorkbook(get_fname(path))   

def process(fqdn,user,pwd,path,args):

    if (args.list):
        try: 
            response = SupportPackage.get_bdb_names(fqdn,user,pwd)
            if (args.json):
                bdb_info = SupportPackage.deserialize_bdb_info(fqdn,response)
                bdb = {}
                bdb['cluster'] = fqdn
                bdb['databases'] = bdb_info
                print(json.dumps(bdb, indent=4))
            else:
                SupportPackage.tablulate_bdb_info(fqdn,response)
        except Exception as e:
            print(f"Error Getting Database Names:{str(e)}")
    elif (args.license):
        response = SupportPackage.get_license_info(fqdn,user,pwd)
        license = SupportPackage.deserialize_license_info(fqdn,response)
        print(json.dumps(license, indent=4)) 
    else:
        try: 

            if args.bloat:
                reduce_tar_size = False                 
            else:
                print("Agressively Optimizing Support Package Size")
                reduce_tar_size = True
                   
            SupportPackage.download_package(fqdn, user,pwd,path,0,reduce_tar_size) 
        
            keep = int(args.keep) if (args.keep is not None) else 1

            sort_and_keep_latest_files(path,f'debuginfo.{fqdn}',keep)    
        
        except Exception as e:
            print(f"Fatal Error: {str(e)}")
            exit(-1)
    return


#
# Process command arguments for specified fqdn
#
def process_args_single_fqdn(fqdn,args,path):
        if (args.user is not None):
            user = args.user
            if (args.pwd is None):
                print("Missing Password")
                exit(-1)
            else:
                pwd = args.pwd
        else:
            try:
                user,pwd = CredentialVault.decrypt_credentials(args.fqdn)
            except Exception as e:
                print(f"Fatal Error: {str(e)}")
                exit(-1)
        try:
            process(fqdn,user,pwd,path,args)
        except Exception as e:
            print(f"Fatal Error: {str(e)}")
            exit(-1)


def main():
    parser = argparse.ArgumentParser(description="Download a support package")

    parser.add_argument("fqdn", help="Fully Qualified Domain Name of the Server (or all)") 
    parser.add_argument("--user", help="Username for authentication")
    parser.add_argument("--pwd", help="Password for Authentication")
    parser.add_argument("--path", help="Folder path for saving Output Files")
    parser.add_argument("--keep",help="Number of Output files to keep")
    parser.add_argument("--bloat",action='store_true',help="Make no attempt to reduce the Package Size") 
    parser.add_argument("--list",action='store_true',help="List Databases Id and Names")
    parser.add_argument("--license",action='store_true',help="List Databases Id and Names")
    parser.add_argument("--json",action='store_true',help="Format Database Output List in Json")
    parser.add_argument("--xls",action='store_true',help="Generate Excel Inventory Report For All Clusters")
    
    args = parser.parse_args()
    user = ''
    pwd = '' 
    fqdn = args.fqdn

    if args.path:
        path = args.path
    else:
        path = "output"   

    if fqdn != 'all':
        process_args_single_fqdn(fqdn,args,path)
        '''
        if (args.user is not None):
            user = args.user
            if (args.pwd is None):
                print("Missing Password")
                exit(-1)
            else:
                pwd = args.pwd
        else:
            try:
                user,pwd = CredentialVault.decrypt_credentials(args.fqdn)
            except Exception as e:
                print(f"Fatal Error: {str(e)}")
                exit(-1)
        try:
            process(fqdn,user,pwd,path,args)
        except Exception as e:
            print(f"Fatal Error: {str(e)}")
            exit(-1)
       '''     
    else:
        if not args.xls:
            fqdns = FQDNs.get()
            for fqdn in fqdns:
                try:
                    user,pwd = CredentialVault.decrypt_credentials(fqdn)
                    process(fqdn,user,pwd,path,args) 
                except Exception as e:
                    print(f"Error during Request for {fqdn}")
        else:
            xls(path)
            keep = int(args.keep) if (args.keep is not None) else 5
            sort_and_keep_latest_files(path,"inventory",keep)    
    
if __name__ == "__main__":

     main()

