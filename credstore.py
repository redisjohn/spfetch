#!/usr/bin/python3
"""Redis Enterprise Credential Manager"""

import argparse
import json
import re
import sys
from lib.credential_vault import CredentialVault
from lib.key_vault import KeyVault
from lib.resolver  import Resolver

import os

def list_files_in_folder(folder_path):
    try:
        # Get a list of all files in the folder
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        return files
    except FileNotFoundError:
        print(f"Error: The folder '{folder_path}' does not exist.")
        return []
    except PermissionError:
        print(f"Error: Permission denied to access '{folder_path}'.")
        return []


def validate_fqdn(fqdn):
 
    # Ensure the FQDN is not too long
    if len(fqdn) > 253:
        return False

    # Regular expression for a valid label in an FQDN
    label_regex = re.compile(r'^(?!-)[A-Za-z0-9-]{1,63}(?<!-)$')

    # Split the FQDN into labels
    labels = fqdn.split(".")

    # Each label must match the regex, and the FQDN must have at least two labels
    if len(labels) < 2 or not all(label_regex.match(label) for label in labels):
        return False

    return True

def confirmChoice():
    choice = input("Confirm [Y/N] ").lower()
    if (choice) != "y":
        exit(0)


def initialize_vault():
    try:
        if KeyVault.has_key():
            print("Vault has already been initialized")
        else:
            KeyVault.set_key()
            print("Secure this Secret Key")
            print(KeyVault.get_key())
    except Exception as e:
        print(f"Fatal Error: {str(e)}")
        exit(-1)


def add_credentials(cluster, user, pwd, vault_path="vault"):
    try:
        CredentialVault.encrypt_credentials(cluster, user, pwd)
        print(f"{cluster} credentials add to vault")
    except Exception as e:
        print(f"Fatal Error: {str(e)}")
        exit(-1)


def get_credentials(cluster, vault_path="vault"):
    try:
        user, pwd = CredentialVault.decrypt_credentials(cluster)
        print(f"U=({user}) P=({pwd})")
    except Exception as e:
        print(f"Fatal Error: {str(e)}")
        exit(-1)


def reset_vault():
    try:
        KeyVault.delete_key()
        print("Secret Deleted from System Keyring")
    except Exception as e:
        print(f"Fatal Error: {str(e)}")
        exit(-1)


def recover_vault(secret):
    try:
        print("Recovering the vault...")
        KeyVault.force_key(secret)
        print("Secret replaced on System Keyring")
    except Exception as e:
        print(f"Fatal Error: {str(e)}")
        exit(-1)


def update_api_key(key):
    CredentialVault.encrypt_credentials(".api.key", "key", key)


def main():
    parser = argparse.ArgumentParser(
        description="Redis Enterprise Cluster Credentials Encrypted Store"
    )
    subparsers = parser.add_subparsers(
        dest="command", help="Available commands")

    # Subparser for the 'init' command
    parser_init = subparsers.add_parser("init", help="Initialize the vault")

    # Subparser for the 'add' command
    parser_add = subparsers.add_parser(
        "add", help="Add encrypted credentials for a cluster"
    )
    parser_add.add_argument("--fqdn", help="Cluster FQDN", required=True)
    parser_add.add_argument("--ip", help="Cluster IP Address", required=False)
    parser_add.add_argument("--user", help="Username", required=True)
    parser_add.add_argument("--pwd", help="Password", required=True)
    # parser_add.add_argument("--path", default="vault", help="Vault path (default: vault)")
    # Subparser for the get command
    parser_add = subparsers.add_parser(
        "get", help="Get Credentials for a cluster")
    parser_add.add_argument("--fqdn", help="Cluster FQDN", required=True)
    # parser_add.add_argument("--path", default="vault", help="Vault path (default: vault)")
    # Subparser for the 'recover' command
    parser_recover = subparsers.add_parser(
        "recover", help="Recovery Vault from Secret")
    parser_recover.add_argument(
        "--secret", help="Secret key for vault recovery", required=True
    )
    # subparser for the 'apikey' command
    parser_apikey = subparsers.add_parser("apikey", help="Save Upload API Key")
    parser_apikey.add_argument("--key", help="API Key", required=True)

    # subparser for reset command
    parser_recover = subparsers.add_parser("reset", help="Delete Vault Secret")

    # Subparser for list command    
    parser_list = subparsers.add_parser("list", help="List FQDNs in Vault")

    parser_list = subparsers.add_parser("del", help="Delete an FQDN in the Vault")
    parser_list.add_argument("--fqdn", help="fdqn to remove")


    args = parser.parse_args()

    if args.command == "init":
        initialize_vault()    
    elif args.command == "add":
        if not validate_fqdn(args.fqdn):
            print("Invalid fqdn format")
            sys.exit(-1)
        add_credentials(args.fqdn, args.user, args.pwd)
        if args.ip:
            resolver = Resolver()
            resolver.load()
            resolver.saveHost(args.fqdn, args.ip)
            resolver.persist()
    elif args.command == "get":
        get_credentials(args.fqdn)
    elif args.command == "reset":
        print("This will remove the vault secret from the system keyring")
        confirmChoice()
        reset_vault()
    elif args.command == "recover":
        print("This will replace the vault secret from the system keyring")
        confirmChoice()
        recover_vault(args.secret)
    elif args.command == "apikey":
        update_api_key(args.key)
        print("API Key Saved")
    elif args.command == "list":
        fqdn_list = []
        for fqdn in list_files_in_folder("vault"):            
            if (validate_fqdn(fqdn)):
                fqdn_list.append(fqdn)
        print(json.dumps(fqdn_list,indent=3))
    elif args.command == "del":
        print(f"Delete ({args.fqdn})")
        confirmChoice()
        fname = f"vault/{args.fqdn}"
        if os.path.exists(fname):
            print(f"deleting entry({args.fqdn})")
            os.remove(fname)
        else:
            print(f"no matching fqdn")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
