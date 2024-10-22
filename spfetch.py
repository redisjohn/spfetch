
import argparse
from SupportPackage import SupportPackage
from CredentialVault import CredentialVault
from Fqdns import FQDNs
import os
import re
import Fqdns

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
            print(f"deleting {fname}")
            #os.remove(fname)

def main():
    parser = argparse.ArgumentParser(description="Download a support package")

    parser.add_argument("fqdn", help="Fully Qualified Domain Name of the server")
    parser.add_argument("--user", help="Username for authentication")
    parser.add_argument("--pwd", help="Password for authentication")
    parser.add_argument("--path", help="Folder path for saving package")
    parser.add_argument("--keep",help="Number of Packages to keep")
    parser.add_argument("--list",action='store_true',help="List Databases Id and Names")
    parser.add_argument("--license",action='store_true',help="List Databases Id and Names")
    parser.add_argument("--json",action='store_true',help="Format Database Output List in Json")
    
    args = parser.parse_args()
    user = ''
    pwd = '' 

    if args.fqdn == 'all':
        fqdns = FQDNs.get()
        print(fqdns) 
        os._exit(0)
    if args.path:
        path = args.path
    else:
        path = "output"   

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

    if (args.list):
        try: 
            response = SupportPackage.get_bdb_names(args.fqdn,user,pwd)
            if (args.json):
                SupportPackage.deserialize_bdb_info(args.fqdn,response)
            else:
                SupportPackage.tablulate_bdb_info(response)
        except Exception as e:
            print(f"Error Getting Database Names:{str(e)}")
    elif (args.license):
        response = SupportPackage.get_license_info(args.fqdn,user,pwd)
        SupportPackage.deserialize_license_info(args.fqdn,response)
    else:
        try: 
            SupportPackage.download_package(args.fqdn, user,pwd,path) 
            if (args.keep is not None):
                sort_and_keep_latest_files(path,args.fqdn,int(args.keep))    
        
        except Exception as e:
            print(f"Fatal Error: {str(e)}")
            exit(-1)


if __name__ == "__main__":

     main()

