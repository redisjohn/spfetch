"""resolver module"""
import os
import json

class Resolver:
    """resolver class"""
    def __init__(self):
        self.resolver = {}

    def save_host(self, fqdn, ip):
        """update host"""
        if not isinstance(fqdn, str) or not isinstance(ip, str):
            raise ValueError("Both fqdn and ip must be strings.")
        fqdn = fqdn.strip().lower()
        self.resolver[fqdn] = ip

    def persist(self, filename='resolver.json'):
        """persist file"""
        try:
            with open(filename, 'w',encoding='utf-8') as file:
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
            with open(filename, 'r',encoding="utf-8") as file:
                self.resolver = json.load(file)
            #print(f"Resolver dictionary has been loaded from {filename}.")
        except Exception as e:
            print(f"An error occurred while loading: {e}")

    def get(self, fqdn):
        """resolve fqdn"""
        fqdn = fqdn.strip().lower()
        return self.resolver.get(fqdn, None)
