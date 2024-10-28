
# Redis Enterprise spfetch  (Automate Support Package Retrieval)


spfetch is a utility for quickly downloading Redis support packages and generating audit reports for Redis Enterprise Software deployments.  
  
spfetch uses a credential vault to secure credentials.  This allows automated scripts to use spfetch in other tooling without having to expose username and passwords in plain text.  


## Quick Start
	
1. Install the Software

    	apt update 
    	apt install python 
		apt install git
    	pip install keyring
    	pip install cryptography
		pip install openpyxl
		git pull https://github.com/redisjohn/spfetch
    
1. Initialize the Credential Vault 

	    credstore.py init 

1. Add cluster credentials to the vault. 

    	credstore.py add cluster1.mydomain.com --user redisuser --pass mypassword

1.	To fetch a support Package

		spfetch.py {cluster-fqdn}
	
1.  The packages are located in the "output" folder.  


## spfetch.py  Redis Enterprise Auditing Tool

    usage: spfetch.py [-h] [--user USER] [--pwd PWD] [--path PATH] [--keep KEEP] [--bloat] [--list] [--license] [--json] [--xls] fqdn
    
    Redis Enterprise Audit Tool
    
    positional arguments:
      fqdn Fully Qualified Domain Name of Cluster (wildcards supported if credentials in vault))
    
    options:
      -h, --help    show this help message and exit
      --user USER  	Username for authentication
      --pwd PWD		Password for Authentication
      --path PATH  	Folder path for saving Output Files
      --keep KEEP  	Number of Output files to keep
      --bloat  		Make no attempt to reduce the Package Size
      --list   		List Databases Id and Names
	  --json   		Format Database Output List in Json
      --license 	List Databases Id and Names      
      --xls			Generate Excel Inventory Report For All Clusters


#### Explicitly Providing Credentials

The only positional argument required to spfetch is a cluster fully qualified domain name.  If the credential vault has not been initialized or the cluster has not been added to the vault, a user name and password is required.   

    $spfetch.py  cluster.redis.test --user test@myorg.com --pwd mypassword 

    2024-10-28 11:49:03,spfetch,INFO,(cluster.redis.test):Agressively Optimizing Support Package Size
    2024-10-28 11:49:03,spfetch,INFO,(cluster.redis.test):Starting Download
	2024-10-28 11:50:18,spfetch,INFO,(cluster.redis.test):Reducing Package Size
	2024-10-28 11:50:32,spfetch,INFO,(cluster.redis.test):Original tar size: 214136954 bytes
	2024-10-28 11:50:32,spfetch,INFO,(cluster.redis.test):New tar size: 2039395 bytes
	2024-10-28 11:50:32,spfetch,INFO,(cluster.redis.test):Storage savings: 212097559 bytes
	2024-10-28 11:50:32,spfetch,INFO,(cluster.redis.test):Support package downloaded successfully.
	2024-10-28 11:50:32,spfetch,INFO,Purging Old Version:(output\debuginfo.cluster.redis.test_20241028112421.tar.gz)   


#### Optimization of support package size

spfetch by default will attempt to optimize a support package output by trimming log files.  This is the default behavior.  
To bypass optimization using the `--bloat ` flag.

#### Overriding support package download location

spfetch by default will store all output generated in the output folder under the main spfetch directory.  To override this location use the `--path` flag.    


#### Using Wildcards with the Credential Vault

If the credential vault is used, wild cards can be used to select a subset of FQDNs that are in the present in the vault.  This allows for easy retrieval of multiple support packages.   

Some examples of supported wild carding.

   	rlec*
	* 
    *dc1*
    *.net 


#### Batch processing Support Packages

It is easy to use wild cards to download multiple support packages at once.  

    
    $spfetch.py *.ixaac.net   
    2024-10-28 11:53:54,spfetch,INFO,(rlec1.ixaac.net):Agressively Optimizing Support Package Size
    2024-10-28 11:53:54,spfetch,INFO,(rlec1.ixaac.net):Starting Download
    2024-10-28 11:55:09,spfetch,INFO,(rlec1.ixaac.net):Reducing Package Size
    2024-10-28 11:55:22,spfetch,INFO,(rlec1.ixaac.net):Original tar size: 214159442 bytes
    2024-10-28 11:55:22,spfetch,INFO,(rlec1.ixaac.net):New tar size: 2041851 bytes
    2024-10-28 11:55:22,spfetch,INFO,(rlec1.ixaac.net):Storage savings: 212117591 bytes
    2024-10-28 11:55:22,spfetch,INFO,(rlec1.ixaac.net):Support package downloaded successfully.
    2024-10-28 11:55:22,spfetch,INFO,Purging Old Version:(output\debuginfo.rlec1.ixaac.net_20241028111754.tar.gz)
    2024-10-28 11:55:22,spfetch,INFO,(rlec2.ixaac.net):Agressively Optimizing Support Package Size
    2024-10-28 11:55:22,spfetch,INFO,(rlec2.ixaac.net):Starting Download
    2024-10-28 11:56:37,spfetch,INFO,(rlec2.ixaac.net):Reducing Package Size
    2024-10-28 11:56:50,spfetch,INFO,(rlec2.ixaac.net):Original tar size: 214176922 bytes
    2024-10-28 11:56:50,spfetch,INFO,(rlec2.ixaac.net):New tar size: 2043745 bytes
    2024-10-28 11:56:50,spfetch,INFO,(rlec2.ixaac.net):Storage savings: 212133177 bytes
    2024-10-28 11:56:50,spfetch,INFO,(rlec2.ixaac.net):Support package downloaded successfully.
    2024-10-28 11:56:50,spfetch,INFO,Purging Old Version:(output\debuginfo.rlec2.ixaac.net_20241028111922.tar.gz)
	2024-10-28 11:56:50,spfetch,INFO,(rlec3.ixaac.net):Starting Download
	2024-10-28 11:58:04,spfetch,INFO,(rlec3.ixaac.net):Reducing Package Size
	2024-10-28 11:58:18,spfetch,INFO,(rlec3.ixaac.net):Original tar size: 214189015 bytes
	2024-10-28 11:58:18,spfetch,INFO,(rlec3.ixaac.net):New tar size: 2044389 bytes
	2024-10-28 11:58:18,spfetch,INFO,(rlec3.ixaac.net):Storage savings: 212144626 bytes
	2024-10-28 11:58:18,spfetch,INFO,(rlec3.ixaac.net):Support package downloaded successfully.
	2024-10-28 11:58:18,spfetch,INFO,Purging Old Version:(output\debuginfo.rlec3.ixaac.net_20241028112621.tar.gz)    
    
#### Auditing Deployments

spfetch provides several other functions to audit cluster deployments. 

The license command provides a quick list of license information for one or more clusters. 

    $spfetch.py --license *
    {
    "cluster": "cluster.redis.test",
    "expired": true,
    "expiration": "2024-10-01",
    "shards_limit": 500,
    "ram_shards": 3,
    "flash_shards": 0
    }
    {
    "cluster": "rlec1.ixaac.net",
    "expired": false,
    "expiration": "2025-07-01",
    "shards_limit": 10,
    "ram_shards": 9,
    "flash_shards": 0
    }
    {
    "cluster": "rlec2.ixaac.net",
    "expired": false,
    "expiration": "2025-07-01",
    "shards_limit": 35,
    "ram_shards": 35,
    "flash_shards": 0
    }
    {
    "cluster": "rlec3.ixaac.net",
    "expired": false,
    "expiration": "2025-10-01",
    "shards_limit": 20,
    "ram_shards": 0,
    "flash_shards": 10
    }

#### Getting database inventory for a cluster. 

To get a quick summary of databases in a cluster.  (You can also use wild cards with this command for any clusters with credentials stored in the vault)

    $spfetch.py --list cluster.redis.test

	cluster.redis.test
	Id  Name    Version Shards
	--------------------------
	1    test    7.2.3     2
	2    test2   7.2.3     1
    

To get a more detailed summary using the --json flag 

		$spfetch.py --list --json cluster.redis.test 
		{
	    "cluster": "cluster.redis.test",
	    "databases": [
	        {
	            "Id": 1,
	            "Name": "test",
	            "Version": "7.2.3",
	            "Total Shards": 2,
	            "High Availability": true,
	            "Flex": false,
	            "Created": "2024-05-14",
	            "Modified": "2024-09-03",
	            "Persistence": "disabled",
	            "Eviction Policy": "volatile-lru",
	            "CRDB": false,
	            "Modules": "",
	            "TLS": true,
	            "OSS Cluster API": false,
	            "Proxy Policy": "single",
	            "Shard Placement": "dense"
	        },
	        {
	            "Id": 2,
	            "Name": "test2",
	            "Version": "7.2.3",
	            "Total Shards": 1,
	            "High Availability": false,
	            "Flex": false,
	            "Created": "2024-09-20",
	            "Modified": "2024-09-20",
	            "Persistence": "disabled",
	            "Eviction Policy": "volatile-lru",
	            "CRDB": false,
	            "Modules": "",
	            "TLS": false,
	            "OSS Cluster API": false,
	            "Proxy Policy": "single",
	            "Shard Placement": "dense"
	        }
	    ]
	}


### Generating An Inventory Report of all Deployments

spfetch can generate an up to date inventory of all clusters deployed.  The inventory report is formatted as a multi-sheet excel workbook with multiple sheets. 

The cluster tab includes a list of all clusters.  A tab is created for each cluster showing detailed information including version numbers of database and modules along with other key settings. 

    spfetch.py --xls *
	2024-10-28 12:26:32,spfetch,INFO,Processing Data for:(cluster.redis.test)
	2024-10-28 12:26:32,spfetch,INFO,Processing Data for:(rlec1.ixaac.net)
	2024-10-28 12:26:32,spfetch,INFO,Processing Data for:(rlec2.ixaac.net)
	2024-10-28 12:26:32,spfetch,INFO,Processing Data for:(rlec3.ixaac.net)
	2024-10-28 12:26:32,spfetch,INFO,Workbook saved as 'output\inventory_20241028122632.xlsx'.
	2024-10-28 12:26:32,spfetch,INFO,Purging Old Version:(output\inventory_20241028094251.xlsx)



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

	credstore.py init

You should save the secret in a secure location.  This will allow you to move the credentials vault to another system if needed in the future.  

Once the vault is initialized you can store encrypted credentials for each cluster. 

	credstore.py add {fqdn} --user {username} --pwd {password} 

#### Moving the Credential Vault to another System

To restore the vault to a different system, you must have a backup of the vault directory and have the secret key generated when the vault was initiated.   After the vault directory is restored on the new system, run the following command:

	credstore.py recover {secretkey}  






