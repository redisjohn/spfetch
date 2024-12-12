"""Keyring Module"""
import keyring
from cryptography.fernet import Fernet


class MissingVaultKey(Exception):
    """MissingVault Key Exception"""
    pass


class KeyVault:
    """KeyVault Class"""
    key_ring_service = "RedisEnterpriseSupportPackagerMgr"
    key_ring_username = "MasterKey"

    @staticmethod
    def has_key():
        """Check for Presence of Key in Vault"""
        password = keyring.get_password(
            KeyVault.key_ring_service,
            KeyVault.key_ring_username)
        if password is not None:
            return True
        else:
            return False

    @staticmethod
    def set_key():
        """Set Key in Vault"""
        if KeyVault.has_key() is not True:
            KeyVault.key = Fernet.generate_key().decode()
            keyring.set_password(
                KeyVault.key_ring_service,
                KeyVault.key_ring_username,
                KeyVault.key)
            return True
        else:
            return False

    @staticmethod
    def force_key(keypass):
        """Force secret into keyring"""
        print(keypass)
        keyring.set_password(
            KeyVault.key_ring_service,
            KeyVault.key_ring_username,
            keypass)

    @staticmethod
    def get_key():
        """Get Secret Key from keyring"""
        KeyVault.key = keyring.get_password(
            KeyVault.key_ring_service,
            KeyVault.key_ring_username)
        if KeyVault.key is None:
            raise MissingVaultKey("Missing Vault Key")
        return KeyVault.key

    @staticmethod
    def delete_key():
        """Delete Secret from Keyring"""
        keyring.delete_password(
            KeyVault.key_ring_service,
            KeyVault.key_ring_username)
