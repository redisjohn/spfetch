import os
import re

class FQDNs:
    # FQDN regex pattern: at least one label, a dot, and a top-level domain
    FQDN_PATTERN = re.compile(r'^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$')
    
    @staticmethod
    def get(directory_path="vault"):
        fqdn_files = []

        # Iterate over each file in the directory
        for filename in os.listdir(directory_path):
            # Check if the filename matches the FQDN pattern
            if FQDNs.FQDN_PATTERN.match(filename):
                fqdn_files.append(filename)

        return fqdn_files