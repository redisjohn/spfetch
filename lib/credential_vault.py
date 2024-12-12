"""Credential Vault Module"""
import os
from cryptography.fernet import Fernet
from lib.key_vault import KeyVault


class CredentialVault:
    """Credential Vault Class"""
    vault_dir = "vault"

    @staticmethod
    def get_vault_dir():
        """Get Vault Directory"""
        if not os.path.exists(CredentialVault.vault_dir):
            os.makedirs(CredentialVault.vault_dir)
        return CredentialVault.vault_dir

    @staticmethod
    def encrypt_credentials(cluster_fqdn, username, password):
        """Encrypt Credentials"""
        cipher_suite = Fernet(KeyVault.get_key())
        encrypted_username = cipher_suite.encrypt(username.encode()).decode()
        encrypted_password = cipher_suite.encrypt(password.encode()).decode()
        fname = os.path.join(CredentialVault.get_vault_dir(), cluster_fqdn)
        with open(fname, 'w', encoding='utf-8') as file:
            file.write(encrypted_username + "\n")
            file.write(encrypted_password + "\n")

    @staticmethod
    def decrypt_credentials(cluster_fqdn):
        """Decrypt Credentials"""
        fname = os.path.join(CredentialVault.get_vault_dir(), cluster_fqdn)
        with open(fname, 'r', encoding='utf-8') as file:
            encrypted_username = file.readline()
            encrypted_password = file.readline()
            cipher_suite = Fernet(KeyVault.get_key())
        username = cipher_suite.decrypt(encrypted_username.encode()).decode()
        password = cipher_suite.decrypt(encrypted_password.encode()).decode()
        return username, password
    