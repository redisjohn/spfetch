# Release Notes

## Version 20250415  (April 15, 2025)

* Added support for pyinstaller to allow building standalone executables files to allow running on machines without python dependencies. 

* Enhanced the audit report. 

    - Cluster Tab 
    
        * Added license owner and cluster name issued for license.   
        * Add Rackaware field
        
    - Added Consolidate Nodes Tab to include detailed information about node in each cluster by cluster. Include hardware infomration and list of shards found on each node.   

    - Added Consolidated Shard Tab to include detailed information about each shard by cluster and database.

    - Added Certificate Tab to include detailed information on cluster and client certificates by fqdn including subject, issuer and expiration date by cluster. 

    - Add Roles, ACL, and Permissions Tabs to include information Roles, ACLs and 
    Permissions by cluster.

    - Added Cipher tab to include information about Ciphers by control and data plan by cluster.

    - The earlier versions included a database tab for each cluster.  To allow support for larger fleets, the database information has been consolidated to one tab with all databases by fqdn.  

    - The following fields have been added to the database tab. 
        * External and Internal Endpoints
        * Authentication Method
        * Memory allocated in GiB
 