# rflat  (Redis Enterprise Fleet Auditing Tool)

----------

rflat is a utility for quickly downloading Redis Enterprise support packages and provide audit reporting for a fleet of  Redis Enterprise Clusters.

rflat accesses a Redis Enterprise Cluster using the Redis Enterprise Software API.  This requires a valid Redis Enterprise user and password for each cluster to be used.  This can be supplied explicitly on the command line but using the credential vault is recommended.  

credstore is a companion utility that works with rflat to manage credentials. credstore encrypts and stores credentials that can be retrieved and used by rflat.  This allows automated scripts to use rflat in other tooling without having to expose user names and passwords in plain text.  It also provides a mechanism to collect support package and inventory information across an entire fleet of clusters using a single command.  

These tools have been developed using python.
  
```sh
 ./rflat -h
 usage: rflat [-h] [--user USER] [--pwd PWD] [--path PATH] [--db DB] [--upload] [--nosave] [--keep KEEP] [--bloat] [--dryrun] [--list] [--json] [--license] [--xls] fqdn

 Redis Enterprise Audit Tool V24.1212

 positional arguments:
  fqdn         Fully Qualified Domain Name of Cluster (wildcards supported if credentials in vault)

 options:
   -h, --help   show this help message and exit
   --user USER  Username for authentication
   --pwd PWD    Password for Authentication
   --path PATH  Folder path for saving Output Files
   --db DB      Database Id
   --upload     Upload Package to Redis.io (requires API KEY)
   --nosave     Do not save support package to disk (works only with --upload
   --keep KEEP  Number of Output files to keep
   --bloat      Make no attempt to reduce the Package Size
   --dryrun     Do a dryrun for testing
   --list       List Databases Id and Names
   --json       Format database output list in Json
   --license    List Databases Id and Names
   --xls        Generate Excel Inventory Report For All Clusters`
 ```

----------

## Quick Start

1. Ensure you have python 3.8 or higher.

1. Ensure you have git installed.

1. Retrieve the code from Github

```sh
git clone https://github.com/redisjohn/spfetch
```

1. Install dependencies

```sh
  pip install -r requirements.txt
```

1. For Linux, the following script is optional but will setup symbolic links and ensure all the python scripts can be executed.
  
```sh
  ./install.sh
```

1. Initialize the Credential Vault

```sh
     ./credstore init 
```
  
 If this command fails on linux, run the following command:
 
```sh
  pip install keyrings.alt
```

1. Add cluster credentials to the vault.

  If you are using DNS:
  
```sh
     ./credstore  add --fqdn cluster1.mydomain.com --user redisuser --pwd mypassword
```
 
  If you are not Using DNS, specify the --ip flag with the IP address of the cluster's primary (master) node. 

```sh
     ./credstore  add --fqdn cluster1.mydomain.com --user redisuser --pwd mypassword --ip 10.7.8.6
```

1. To fetch a support Package

```sh  
  ./rflat cluster1.mydomain.com
```

1. The packages are located in the "output" folder.  

----------

## Deep Dive

- [rflat  (Redis Enterprise Fleet Auditing Tool)](#rflat--redis-enterprise-fleet-auditing-tool)
  - [Quick Start](#quick-start)
  - [Deep Dive](#deep-dive)
      - [Requirements for Redis Enterprise User Permissions](#requirements-for-redis-enterprise-user-permissions)
      - [Explicitly Providing Credentials](#explicitly-providing-credentials)
      - [Using the Credential Vault](#using-the-credential-vault)
      - [Using Wild Cards with rflat](#using-wild-cards-with-rflat)
        - [Wild card globing (Linux)](#wild-card-globing-linux)
      - [Batch processing Support Packages Downloads](#batch-processing-support-packages-downloads)
      - [Pulling a Support Package for a Single Database](#pulling-a-support-package-for-a-single-database)
      - [Optimization of support package size](#optimization-of-support-package-size)
      - [Overriding support package download location](#overriding-support-package-download-location)
      - [Purging old files](#purging-old-files)
    - [Uploading Support Packages to Redis](#uploading-support-packages-to-redis)
  - [Credentials Management using credstore](#credentials-management-using-credstore)
      - [Initializing the Credential Vault](#initializing-the-credential-vault)
      - [Managing Credentials in environments without DNS](#managing-credentials-in-environments-without-dns)
      - [Removing a cluster from the vault](#removing-a-cluster-from-the-vault)
      - [Moving the Credential Vault to another System](#moving-the-credential-vault-to-another-system)
  - [unbloat](#unbloat)
  - [Considerations for running python](#considerations-for-running-python)
        - [Windows](#windows)
        - [Linux and Mac OS](#linux-and-mac-os)

#### Requirements for Redis Enterprise User Permissions

The user credentials provided must have a Management Role of `DB Member` or higher to access the Redis Software API endpoints used by rflat.

#### Explicitly Providing Credentials

The only positional argument required to rflat is a cluster fully qualified domain name.  If the credential vault has not been initialized or the cluster has not been added to the vault, a user name and password is required.  If you explicit provide credentials, the command line overrides any credentials stored in the vault.  

```sh
    ./rflat  cluster.redis.test --user test@myorg.com --pwd mypassword 

 2024-10-28 11:49:03,rflat,INFO,(cluster.redis.test):Agressively Optimizing Support Package Size
 2024-10-28 11:49:03,rflat,INFO,(cluster.redis.test):Starting Download
 2024-10-28 11:50:18,rflat,INFO,(cluster.redis.test):Reducing Package Size
 2024-10-28 11:50:32,rflat,INFO,(cluster.redis.test):Original tar size: 214136954 bytes
 2024-10-28 11:50:32,rflat,INFO,(cluster.redis.test):New tar size: 2039395 bytes
 2024-10-28 11:50:32,rflat,INFO,(cluster.redis.test):Storage savings: 212097559 bytes
 2024-10-28 11:50:32,rflat,INFO,(cluster.redis.test):Support package downloaded successfully.
 2024-10-28 11:50:32,rflat,INFO,Purging Old Version:(output\debuginfo.cluster.redis.test_20241028112421.tar.gz)   
```

You can also use the IP address of the master node if you specify the username and password.  

```sh
 ./rflat 10.7.0.164 --user test@myorg.com --pwd mypassword
 2024-11-19 12:09:21,rflat,INFO,(10.7.0.164):Agressively Optimizing Support Package Size
 2024-11-19 12:09:21,rflat,INFO,(10.7.0.164):Starting Download
 2024-11-19 12:10:48,rflat,INFO,(10.7.0.164):Reducing Package Size
 2024-11-19 12:11:01,rflat,INFO,(10.7.0.164):Original tar size: 249.38MB
 2024-11-19 12:11:01,rflat,INFO,(10.7.0.164):New tar size: 2.07MB
 2024-11-19 12:11:01,rflat,INFO,(10.7.0.164):Storage savings: 247.31MB
 2024-11-19 12:11:01,rflat,INFO,(10.7.0.164):Support Package Downloaded and Saved:(output\debuginfo.10.7.0.164_20241119121048.tar.gz)
```

#### Using the Credential Vault

In order to avoid exposing user name and passwords, rflat supports adding cluster credentials to a encrypted vault.  Using this feature also allows the convenience of operating on multiple clusters with one command using wild cards for the fqdn.  If no password is provided, then rflat will automatically check the credentials vault and automatic retrieve the credentials for the specified cluster.  

```sh
  ./rflat cluster.redis.test
```

To configure the credential vault:

The vault must be initialized before it can be used to store credentials

```sh
 ./credstore init 
 ```

Clusters can be added to the vault using the add command:

```sh
 ./crestore add --fqdn cluster.redis.test bob@myorg.com --pwd mypassword
 ```

rflat uses the Redis Enterprise Software REST API ([https://redis.io/docs/latest/operate/rs/references/rest-api/](https://redis.io/docs/latest/operate/rs/references/rest-api/)).   Authentication to this API is done using BASIC AUTH.   The credstore utility is used to encrypt and store user name and passwords that can be retrieved as needed without exposing them in plain text.  

#### Using Wild Cards with rflat

If the credential vault is initalized and populated, wild cards can be used with rflat to select a subset of FQDNs.  This can be used with any rflat operation to process requests against multiple clusters.

Some examples of supported wild carding.

```sh
    rlec*
    *dc1*
    *.net 
    *   
```

##### Wild card globing (Linux)

For Linux using the `*` as wildcard character will not work.  On linux the bash shell will expand the wildcard  before the script is invoked and will cause an error.  

There are several ways to handle this.

You can enclose the wild card in single quotes

```sh
    ./rflat --list '*'  
    ```

You can use a single . to indicate all FQDNs

```sh
 ./rflat --list . 
 ```

You can also put quotes around the FQDN.
Examples:

```sh
./rflat '*.cluster.test'
./rflat 'rl*.net'         
```

You can also disable globing in in the bash shell.

```sh
    $set -o noglob
    ./rflat --list *
```

To re-enable globing in the shell.

```sh
    $set +o noglob
```

For zsh you can prepend noglob to the alias definition to disable globbing for the command.

```sh
alias rflat="noglob rflat"
```
  
#### Batch processing Support Packages Downloads

It is easy to use wild cards to download multiple support packages at once.  

```sh
    ./rflat *.ixaac.net   
    2024-10-28 11:53:54,rflat,INFO,(rlec1.ixaac.net):Agressively Optimizing Support Package Size
    2024-10-28 11:53:54,rflat,INFO,(rlec1.ixaac.net):Starting Download
    2024-10-28 11:55:09,rflat,INFO,(rlec1.ixaac.net):Reducing Package Size
    2024-10-28 11:55:22,rflat,INFO,(rlec1.ixaac.net):Original tar size: 214159442 bytes
    2024-10-28 11:55:22,rflat,INFO,(rlec1.ixaac.net):New tar size: 2041851 bytes
    2024-10-28 11:55:22,rflat,INFO,(rlec1.ixaac.net):Storage savings: 212117591 bytes
    2024-10-28 11:55:22,rflat,INFO,(rlec1.ixaac.net):Support package downloaded successfully.
    2024-10-28 11:55:22,rflat,INFO,Purging Old Version:(output\debuginfo.rlec1.ixaac.net_20241028111754.tar.gz)
    2024-10-28 11:55:22,rflat,INFO,(rlec2.ixaac.net):Agressively Optimizing Support Package Size
    2024-10-28 11:55:22,rflat,INFO,(rlec2.ixaac.net):Starting Download
    2024-10-28 11:56:37,rflat,INFO,(rlec2.ixaac.net):Reducing Package Size
    2024-10-28 11:56:50,rflat,INFO,(rlec2.ixaac.net):Original tar size: 214176922 bytes
    2024-10-28 11:56:50,rflat,INFO,(rlec2.ixaac.net):New tar size: 2043745 bytes
    2024-10-28 11:56:50,rflat,INFO,(rlec2.ixaac.net):Storage savings: 212133177 bytes
    2024-10-28 11:56:50,rflat,INFO,(rlec2.ixaac.net):Support package downloaded successfully.
    2024-10-28 11:56:50,rflat,INFO,Purging Old Version:(output\debuginfo.rlec2.ixaac.net_20241028111922.tar.gz)
 2024-10-28 11:56:50,rflat,INFO,(rlec3.ixaac.net):Starting Download
 2024-10-28 11:58:04,rflat,INFO,(rlec3.ixaac.net):Reducing Package Size
 2024-10-28 11:58:18,rflat,INFO,(rlec3.ixaac.net):Original tar size: 214189015 bytes
 2024-10-28 11:58:18,rflat,INFO,(rlec3.ixaac.net):New tar size: 2044389 bytes
 2024-10-28 11:58:18,rflat,INFO,(rlec3.ixaac.net):Storage savings: 212144626 bytes
 2024-10-28 11:58:18,rflat,INFO,(rlec3.ixaac.net):Support package downloaded successfully.
 2024-10-28 11:58:18,rflat,INFO,Purging Old Version:(output\debuginfo.rlec3.ixaac.net_20241028112621.tar.gz)    
 ```

#### Pulling a Support Package for a Single Database

You can use the --db flag to pull a support package for a single database.  This helps reduce the size of the support package.  There is still full cluster topology and using this flag will produce the smallest possible support package prior to size optmization that is done.

```sh
 ./rflat --db 1  cluster.redis.test 
 ```

You can get a list of database ids using the following command:

```sh
 ./rflat --list cluster.redis.test
 ```

#### Optimization of support package size

rflat by default will attempt to optimize a support package output by trimming log files.  This is the default behavior.  To bypass optimization using the `--bloat` flag.   This is not compatible for use with `--upload`

#### Overriding support package download location

rflat by default will store all output generated in the `output`folder under the main rflat directory.  To override this location use the `--path` flag.  

```sh
 ./rflat --path /tmp cluster.redis.test 
 ```

#### Purging old files

rflat will remove all old versions of a support packages by default each time is generates an updated copy.  You can override the number of old version using the `--keep` flag.   For inventory reports, the default value is 5.

```sh
    ./rflat rlec4.ixaac.net --keep 3
    ./rflat --xls * --keep 2 
    ```

    
#### Auditing Deployments

rflat provides several other functions to audit cluster deployments.

The license command provides a quick list of license information for one or more clusters.

```sh
    ./rlflat --license *
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
    ```

#### Getting database inventory for a cluster

To get a quick summary of databases in a cluster.  (You can also use wild cards with this command for any clusters with credentials stored in the vault)

```sh
    ./rflat --list cluster.redis.test

 cluster.redis.test
 Id  Name    Version Shards
 --------------------------
 1    test    7.2.3     2
 2    test2   7.2.3     1
    ```
    

To get a more detailed summary using the --json flag

```sh
  ./rflat --list --json cluster.redis.test 
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
 ```

### Uploading Support Packages to Redis

In addition to downloading support packages, you can also upload support packages to Redis.  To upload a support package, an API key is required.   Please contact your Redis Enterprise Account Representative to obtain an API key.  Once you have an API key, it must be stored in the credentials vault.  

```sh
      ./credstore apikey --key 04040403828489492302ac93d934c9c934c9c349
```

To upload a support package you can use the `--upload` flag.  

```sh
   ./rflat --db 1 --upload  cluster.redis.test
   ```

If you do not wish to save the support package to disk, you can use the `--nosave` flag.

```sh
      ./rflat --db 1 --upload --nosave cluster.redis.test     
      ```

----------

### Generating An Inventory Report for a Fleet of Clusters

rflat can generate an up to date inventory of all clusters deployed.  The inventory report is formatted as a multi-sheet excel workbook with multiple sheets.

The cluster tab includes a list of all clusters.  A tab is created for each cluster showing detailed information including version numbers of database and modules along with other key settings.

```sh
    ./rflat --xls *
 2024-10-28 12:26:32,rflat,INFO,Processing Data for:(cluster.redis.test)
 2024-10-28 12:26:32,rflat,INFO,Processing Data for:(rlec1.ixaac.net)
 2024-10-28 12:26:32,rflat,INFO,Processing Data for:(rlec2.ixaac.net)
 2024-10-28 12:26:32,rflat,INFO,Processing Data for:(rlec3.ixaac.net)
 2024-10-28 12:26:32,rflat,INFO,Workbook saved as 'output\inventory_20241028122632.xlsx'.
 2024-10-28 12:26:32,rflat,INFO,Purging Old Version:(output\inventory_20241028094251.xlsx)
 ```

----------

## Credentials Management using credstore

```sh
   usage: credstore.py [-h] {init,add,get,recover,apikey,reset,list,del} ...
  
  Redis Enterprise Cluster Credentials Encrypted Store
  
  positional arguments:
    {init,add,get,recover,apikey,reset,list,del}
                          Available commands
      init                Initialize the vault
      add                 Add encrypted credentials for a cluster
      get                 Get Credentials for a cluster
      recover             Recovery Vault from Secret
      apikey              Save Upload API Key
      reset               Delete Vault Secret
      list                List FQDNs in Vault
      del                 Delete an FQDN in the Vault
  
  options:
    -h, --help            show this help message and exit
  ```

credstore can be used to manage credentials. It implements a password vault to save all databases credentials. The credentials are encrypted using Fernet, a 128 Bit Symmetric Block Cipher.

The file CredentialVault class found in CreditialVault.py can be used to update the Cipher if required by replacing the `encrypt_credentials` and `decrypt_credentials` methods.  

Encrypted Credentials for each cluster are store in a file in the vault folder.

The secret key for the vault is stored in the system key chain which is local. However, the KeyVault class found in Keyvault.py could be easily modified to support additional cloud based keyring providers.

If the vault needs to be relocated to another machine, the vault can be moved and reused as by inserting the secret into the key chain of the new system.

#### Initializing the Credential Vault

The credstore utility is used to manage credentials.  

To initialize the vault run the following command:

 ```sh
 ./credstore init
 ```

You should save the secret in a secure location.  This will allow you to move the credentials vault to another system if needed in the future.  

Once the vault is initialized you can store encrypted credentials for each cluster.

```sh
 credstore add --fqdn cluster.stark.local --user tony.stark@stark.com --pwd myP@$$W0RD
 ```

#### Managing Credentials in environments without DNS  

The "add" sub command requires the FQDN of the cluster be specified.   The optional IP argument can be used in environments that do not use DNS.  By specifying the internal IP address of the primary node, connections to the Redis Software REST API will be done via the IP address of the primary node instead of the FQDN.  Although, the FQDN is still required, it is arbitrary and will only be used for reporting purposes and will never be resolved by DNS.  This behavior is similar to using a hostname file in Linux.

By default, REST API calls only work on the primary node.   This behavior can be overridden to allow any node in the cluster to always redirect to the primary node using the following rladmin command:

```sh
 rladmin cluster config handle_redirects enabled
```

This will allow any internal IP address of any node in the cluster to be specified.

The file resolver.json contains a persisted dictionary of all full qualified domain names that are resolved by rflat to IP addresses.  This file can be edited to remove or change entries as needed.

```sh
 credstore add [-h] --fqdn FQDN [--ip IP] --user USER --pwd PWD

 options:
   -h, --help   show this help message and exit
   --fqdn FQDN  Cluster FQDN
   --ip IP      Cluster IP Address
   --user USER  Username
   --pwd PWD    Password 
```

Example:

```sh
 credstore add --fqdn cluster.stark.local --ip 10.46.20.1 --user tony.stark@stark.com --pwd myP@$$W0RD
 ```

If the above example, any REST API call for cluster.stark.local will be replaced \with the IP address 10.46.20.1. This address should be the address of the primary node unless redirection is enabled as specified above.

#### Removing a cluster from the vault

Use the delete command to remove a cluster from the vault

```sh
 credstore del --fqdn cluster.stark.local
 ```

#### Moving the Credential Vault to another System

To restore the vault to a different system, you must have a backup of the vault directory and have the secret key generated when the vault was initiated.  If you are not using DNS, you should also copy the resolver.json file which resides in the main rflat directory.  After the vault directory is restored on the new system, run the following command:

```sh
 ./credstore recover {secretkey}  
 ```

## unbloat

For support packages that were not fetched with rflat, you can use unbloat to optimize the size and optionally upload them to redis.  

```sh
 usage: unbloat [-h] [--bloat] [--upload] [--nosave] file
 
 Remove Bloat from Support Packages
 
 positional arguments:
   filePath to the file
 
 options:
   -h, --help   show this help message and exit
   --bloat   Leave it Bloated
   --upload  upload to redis.io
   --nosave  Do not save`
   ```


Example:

```sh
unbloat --upload output\debuginfo.cluster.redis.test_20241108172328.tar.gz 
 
 Filename:(debuginfo.cluster.redis.test_20241108172328.tar.gz)
 2024-11-08 21:02:24,unbloat,INFO,Original tar size: 2.09MB
 2024-11-08 21:02:24,unbloat,INFO,New tar size: 2.09MB
 2024-11-08 21:02:24,unbloat,INFO,:Storage savings: 0.0MB
 2024-11-08 21:02:24,unbloat,INFO,Uploading debuginfo.cluster.redis.test_20241108172328.tar.gz to Redis.io
 2024-11-08 21:02:26,unbloat,INFO,Save:output\unbloat-debuginfo.cluster.redis.test_20241108172328.tar.gz
```

## Considerations for running python

##### Windows

For Windows using the classic command processor (cmd.exe), you can simply type the name of the utility to run it.

```sh
 rflat -h
 ```

For Powershell:

```sh
 .\rflat -h 
 ```

There are batch files for each command line utility that explicitly invoke the python interpreter.  This should alleviate any issues with having multiple versions.

Use System -> Advanced Settings -> Environment Variables to verify the path that corresponds to the python interpreter.   You can also locate python interpreters in Windows using the following commands:

```sh
 where python3
 where python
 ```

##### Linux and Mac OS

For Linux and MacOs, the install.sh script will configure symbolic links to name of the command so that they can be executed by name within bash.  

```sh
  ./rflat -h 
  ```

Each utility start with the following line:

```python
 #!/usr/bin/python3
 ```

This is used to associate the file type.  Run the ./install.sh script to set permission bits and make symbolic links.

To locate versions of python:

```sh
 whereis python3
 ```

This can be modified if your python executable is not in /usr/bin.   However you can also invoke the python interpreter directly to execute any of the scripts.

```sh
 python3 rflat -h 
 ```
