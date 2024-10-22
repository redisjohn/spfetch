import os
import re

class FQDNs:
    # FQDN regex pattern: at least one label, a dot, and a top-level domain
    FQDN_PATTERN = re.compile(r'^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$')
    #FQDN_PATTERN = re.compile(r'^(?!-)[A-Za-z0-9-]+(?<!-)(?:\.[A-Za-z0-9-]+)*(?:\.[A-Za-z]{2,10})$')

    @staticmethod
    def get(directory_path="vault"):
        fqdn_files = []

        # Iterate over each file in the directory
        for filename in os.listdir(directory_path):
            # Check if the filename matches the FQDN pattern
            print(filename)
            if FQDNs.FQDN_PATTERN.match(filename):
                fqdn_files.append(filename)
                print("match")

        return fqdn_files