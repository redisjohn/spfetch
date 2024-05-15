from cryptography.fernet import Fernet
from KeyVault import KeyVault

import os

class CredentialVault:

    vault_dir = "vault"

    @staticmethod
    def getVaultDir():
        if not os.path.exists(CredentialVault.vault_dir):
            os.makedirs(CredentialVault.vault_dir)
        return CredentialVault.vault_dir

    @staticmethod
    def encrypt_credentials(cluster_fqdn,username, password):
        cipher_suite = Fernet(KeyVault.get_key())
        encrypted_username = cipher_suite.encrypt(username.encode()).decode()
        encrypted_password = cipher_suite.encrypt(password.encode()).decode()
        fname = os.path.join(CredentialVault.getVaultDir(),cluster_fqdn)
        with open(fname, 'w') as file:
           file.write(encrypted_username + "\n")
           file.write(encrypted_password + "\n")

    @staticmethod
    def decrypt_credentials(cluster_fqdn):
            
        fname = os.path.join(CredentialVault.getVaultDir(),cluster_fqdn)
        with open(fname, 'r') as file:
            encrypted_username = file.readline()
            encrypted_password = file.readline()            
        cipher_suite = Fernet(KeyVault.get_key())
        username = cipher_suite.decrypt(encrypted_username.encode()).decode()
        password = cipher_suite.decrypt(encrypted_password.encode()).decode()
        return username, password