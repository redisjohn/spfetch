
# Redis Enterprise spfetch  (Automate Support Package Retrieval)


spfetch is a utility for quickly downloading Redis support packages.  It can be used to download support packages ad-hoc as needed or it can be used in conjunction with job scheduling software such as cron to automate periodic retrieval of support packages. 
  

spfetch uses a credential vault to secure credentials.  This allows automated scripts to use spfetch in other tooling without having to expose username and passwords in plain text.  


## Quick Start
	
1. Install the Software

    	apt update 
    	apt install python 
    	pip install keyring
    	pip install filelock
    	pip install cryptography
		git pull {add-git-repo} 
    
1. Initialize the Credential Vault 

	    credstore.py init 

1. Add cluster credentials to the vault. 

    	credstore.py add cluster1.mydomain.com --user redisuser --pass mypassword

1.	To fetch a support Package

		spfetch.py {cluster-fqdn}
	
1.  The packages are located in the "output" folder.  


## spfetch.py  Fetching Support Packages

    usage: spfetch.py [-h] [--user USER] [--pwd PWD] [--path PATH] [--keep KEEP] fqdn
    
    Download a support package
    
    positional arguments:
      fqdn Fully Qualified Domain Name of the server
    
    options:
      -h, --help   show this help message and exit
      --user USER  Username for authentication
      --pwd PWDPassword for authentication
      --path PATH  Folder path for saving package
      --keep KEEP  Number of Packages to keep


## credstore.py Credentials Management
    
    usage: credstore.py [-h] {init,add,get,recover,reset} ...
    
    Redis Enterprise Cluster Credentials Encrypted Store
    
    positional arguments:
      {init,add,get,recover,reset}
    Available commands
    initInitialize the vault
    add Add encrypted credentials for a cluster
    get Get Credentials for a cluster
    recover Recovery Vault from Secret
    reset   Delete Vault Secret
    
    options:
      -h, --helpshow this help message and exit

credstore.py can be used to manage credentials. It implements a password vault to save all databases credentials. The credentials are encrypted using Fernet, a 128 Bit Symmetric Block Cipher. 

The file CredentialVault.py can be used to update the Cipher if required by replacing the `encrypt_credentials` and `decrypt_credentials` methods. 

Encrypted Credentials for each cluster are store in a file in the vault folder.  
The default folder name is vault but the name and location can be overridden. 

The secret key for the vault is stored in the system key chain.  If the vault needs to be relocated to another machine, the vault can be moved and reused as by inserting the secret into the keychain of the new system. 



#### Managing Credentials with credstore 

The credstore utility is used to manage credentials.  

To initialize the vault run the following command:

	credstore init

You should save the secret in a secure location.  This will allow you to move the credentials vault to another system if needed in the future.  

Once the vault is initialized you can store encrypted credentials for each cluster. 

	credstore add {fqdn} --user {username} --pwd {password} 

#### Moving the Credential Vault to another System

To restore the vault to a different system, you must have a backup of the vault directory and have the secret key generated when the vault was initiated.   After the vault directory is restored on the new system, run the following command:

	credstore recover {secretkey}  







