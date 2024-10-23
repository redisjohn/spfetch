
import argparse
from SupportPackage import SupportPackage
from CredentialVault import CredentialVault
from ExcelReportGenerator import ExcelReportGenerator
from Fqdns import FQDNs
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
            print(f"deleting {fname}")
            #os.remove(fname)


def xls():
    licenses = []
    fqdns = FQDNs.get()

 # Create a new instance of the generator
    generator = ExcelReportGenerator()

    # Create a new workbook and add data
    generator.CreateWorkbook()
    generator.CreateSheet("Clusters")

    for fqdn in fqdns:
        try:
            user,pwd = CredentialVault.decrypt_credentials(fqdn)
            # get license info for cluster sheet
            response = SupportPackage.get_license_info(fqdn,user,pwd)
            licenses.append(SupportPackage.deserialize_license_info(fqdn,response)) 
            # create sheet for fqdn 
            response = SupportPackage.get_bdb_names(fqdn,user,pwd)
            bdb_data = SupportPackage.deserialize_bdb_info(fqdn,response)
            generator.CreateSheet(fqdn)
            generator.AddData(fqdn,bdb_data)
        except Exception as e:
            print(f"Error during Request for {fqdn}")

        
    # add licenses to cluster worksheet        
    generator.AddData("Clusters",licenses)     
    #save the workbook   
    generator.SaveWorkbook('inventory.xlsx')

def process(fqdn,user,pwd,path,args):

    if (args.list):
        try: 
            response = SupportPackage.get_bdb_names(fqdn,user,pwd)
            if (args.json):
                bdb_info = SupportPackage.deserialize_bdb_info(fqdn,response)
                print(json.dumps(bdb_info, indent=4))
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
            SupportPackage.download_package(fqdn, user,pwd,path) 
            if (args.keep is not None):
                sort_and_keep_latest_files(path,fqdn,int(args.keep))    
        
        except Exception as e:
            print(f"Fatal Error: {str(e)}")
            exit(-1)
    return

def main():
    parser = argparse.ArgumentParser(description="Download a support package")

    parser.add_argument("fqdn", help="Fully Qualified Domain Name of the Server")
    parser.add_argument("--user", help="Username for authentication")
    parser.add_argument("--pwd", help="Password for authentication")
    parser.add_argument("--path", help="Folder path for saving package")
    parser.add_argument("--keep",help="Number of Packages to keep")
    parser.add_argument("--list",action='store_true',help="List Databases Id and Names")
    parser.add_argument("--license",action='store_true',help="List Databases Id and Names")
    parser.add_argument("--json",action='store_true',help="Format Database Output List in Json")
    parser.add_argument("--xls",action='store_true',help="Generate Excel Inventory Report from vault entries")
    
    args = parser.parse_args()
    user = ''
    pwd = '' 
    fqdn = args.fqdn

    if args.path:
        path = args.path
    else:
        path = "output"   

    if fqdn != 'all':

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
            xls()
    
if __name__ == "__main__":

     main()

