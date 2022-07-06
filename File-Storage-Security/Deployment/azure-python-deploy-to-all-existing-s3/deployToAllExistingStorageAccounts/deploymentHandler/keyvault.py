from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

import utils

def get_secret_from_keyvault(secret_key):
    keyvault_uri = utils.get_config_from_file('keyvault_uri')
    credential = DefaultAzureCredential()
    secret_client = SecretClient(vault_url=keyvault_uri, credential=credential)
    return secret_client.get_secret(secret_key)