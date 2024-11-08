import keyring
from cryptography.fernet import Fernet

class MissingVaultKey(Exception):
    pass

class KeyVault:
    key_ring_service = "RedisEnterpriseSupportPackagerMgr"
    key_ring_username = "MasterKey"

    @staticmethod
    def has_key():
        password = keyring.get_password(KeyVault.key_ring_service,KeyVault.key_ring_username)
        if password is not None:
            return True
        else:
            return False
    @staticmethod
    def set_key():
        if KeyVault.has_key() is not True:
            KeyVault.key = Fernet.generate_key().decode()
            keyring.set_password(KeyVault.key_ring_service,KeyVault.key_ring_username,KeyVault.key)
            return True
        else:
            return False

    @staticmethod
    def force_key(keypass):
        print(keypass)
        keyring.set_password(KeyVault.key_ring_service,KeyVault.key_ring_username,keypass)

    @staticmethod
    def get_key():
        KeyVault.key = keyring.get_password(KeyVault.key_ring_service,KeyVault.key_ring_username)
        if (KeyVault.key is None):
            raise MissingVaultKey("Missing Vault Key")
        return KeyVault.key

    @staticmethod
    def delete_key():
        keyring.delete_password(KeyVault.key_ring_service,KeyVault.key_ring_username)