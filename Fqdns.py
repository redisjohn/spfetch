import os
import re
from CredentialVault import CredentialVault

class FQDNs:
    # FQDN regex pattern: at least one label, a dot, and a top-level domain
    FQDN_PATTERN = re.compile(r'^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$')
    
    @staticmethod
    def match_filenames(filenames, pattern):
        # Escape regex special characters in pattern except '*'
        pattern = re.escape(pattern).replace(r'\*', '.*')
        # Add anchors to match the full string
        regex = re.compile(f'^{pattern}$')
        
        # Filter filenames that match the pattern
        matched_files = [filename for filename in filenames if regex.match(filename)]
        return matched_files


    @staticmethod
    def get(pattern):
        fqdn_files = []

        vault_path = CredentialVault.getVaultDir()
        files = FQDNs.match_filenames(os.listdir(vault_path),pattern)

        for filename in files:
            # Check if the filename matches the FQDN pattern
            if FQDNs.FQDN_PATTERN.match(filename):
                fqdn_files.append(filename)
                
        return fqdn_files
