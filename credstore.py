import argparse
from CredentialVault import CredentialVault
from KeyVault import KeyVault

def confirmChoice():
    choice = input("Confirm [Y/N] ").lower()
    if (choice) != "y":
        exit(0)

def initialize_vault():
    try:
        if (KeyVault.has_key()):
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
        CredentialVault.encrypt_credentials(cluster,user,pwd)
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
        print("Secret Deleted from System Keyring");
    except Exception as e:
        print(f"Fatal Error: {str(e)}")
        exit(-1)

def recover_vault(secret):
    try:
        print("Recovering the vault...")
        KeyVault.force_key(secret)
        print(f"Secret replaced on System Keyring")
    except Exception as e:
        print(f"Fatal Error: {str(e)}")
        exit(-1)

def main():
    parser = argparse.ArgumentParser(description="Redis Enterprise Cluster Credentials Encrypted Store")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Subparser for the 'init' command
    parser_init = subparsers.add_parser("init", help="Initialize the vault")

    # Subparser for the 'add' command
    parser_add = subparsers.add_parser("add", help="Add encrypted credentials for a cluster")
    parser_add.add_argument("--cluster", help="Cluster FQDN",required=True)
    parser_add.add_argument("--user", help="Username", required=True)
    parser_add.add_argument("--pwd", help="Password",required=True)
    parser_add.add_argument("--path", default="vault", help="Vault path (default: vault)")
    # Subparser for the get command
    parser_add = subparsers.add_parser("get", help="Get Credentials for a cluster")
    parser_add.add_argument("--cluster", help="Cluster FQDN",required=True)
    parser_add.add_argument("--path", default="vault", help="Vault path (default: vault)")
    # Subparser for the 'recover' command
    parser_recover = subparsers.add_parser("recover", help="Recovery Vault from Secret")
    parser_recover.add_argument("--secret", help="Secret key for vault recovery",required=True)
    #subprocess for reset command
    parser_recover = subparsers.add_parser("reset", help="Delete Vault Secret")
    args = parser.parse_args()

    if args.command == "init":
        initialize_vault()
    elif args.command == "add":
        add_credentials(args.cluster, args.user, args.pwd, args.path)
    elif args.command == "get":
        get_credentials(args.cluster,args.path)
    elif args.command == "reset":
        print("This will remove the vault secret from the system keyring")
        confirmChoice()
        reset_vault()    
    elif args.command == "recover":
        print("This will replace the vault secret from the system keyring")
        confirmChoice()
        recover_vault(args.secret)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
