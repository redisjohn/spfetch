import os
import json

class Resolver:
    def __init__(self):
        self.resolver = {}

    def saveHost(self, fqdn, ip):
        if not isinstance(fqdn, str) or not isinstance(ip, str):
            raise ValueError("Both fqdn and ip must be strings.")
        fqdn = fqdn.strip().lower()
        self.resolver[fqdn] = ip

    def persist(self, filename='resolver.json'):
        try:
            with open(filename, 'w') as file:
                json.dump(self.resolver, file, indent=4)
            #print(f"Resolver dictionary has been saved to {filename}.")
        except Exception as e:
            print(f"An error occurred while saving: {e}")

    def load(self, filename='resolver.json'):
        """
        Load the resolver dictionary from a JSON file if it exists.
        """
        if not os.path.isfile(filename):
            #print(f"File {filename} does not exist. Starting with an empty resolver dictionary.")
            return

        try:
            with open(filename, 'r') as file:
                self.resolver = json.load(file)
            #print(f"Resolver dictionary has been loaded from {filename}.")
        except Exception as e:
            print(f"An error occurred while loading: {e}")

    def get(self, fqdn):
        fqdn = fqdn.strip().lower()
        return self.resolver.get(fqdn, None)

'''
# Example Usage:
# Initialize the Resolver object
resolver = Resolver()

# Attempt to load without the file existing
resolver.load()  # Should handle missing file gracefully

# Save some entries and persist
resolver.saveHost("example.com", "93.184.216.34")
resolver.saveHost("anotherdomain.com", "192.168.1.1")
resolver.persist()

# Reload the dictionary
resolver.load()

# Verify entries
print("IP for 'example.com':", resolver.get("example.com"))  # Should return "93.184.216.34"
print("IP for 'nonexistent.com':", resolver.get("nonexistent.com"))  # Should return None
'''