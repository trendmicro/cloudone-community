"""
Modified class. Original version can be found at https://raw.githubusercontent.com/Azure-Samples/resource-manager-python-template-deployment/master/deployer.py

Modifications include
    - uuid7 instead of Haikunator, for a shorter random suffix.
    - using dynamic regions for deployment
"""

"""A deployer class to deploy a template on Azure"""
import os.path
import json
from uuid_extensions import uuid7str
from azure.common.credentials import ServicePrincipalCredentials
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import DeploymentMode

import keyvault

class Deployer(object):
    """ Initialize the deployer class with subscription, resource group and public key.

    :raises IOError: If the public key path cannot be read (access or not exists)
    :raises KeyError: If AZURE_CLIENT_ID, AZURE_CLIENT_SECRET or AZURE_TENANT_ID env
        variables or not defined
    """

    def __init__(self, subscription_id, resource_group_name, storage_stack_params):
        self.subscription_id = subscription_id
        self.resource_group_name = resource_group_name
        self.credentials = DefaultAzureCredential(exclude_environment_credential=False)

        print(str(keyvault.get_secret_from_keyvault('FSS-AUTODEPLOY-CLIENT-ID')), str(keyvault.get_secret_from_keyvault('FSS-AUTODEPLOY-CLIENT-SECRET')))

        # print(str(os.environ['AZURE_CLIENT_ID']), str(os.environ['AZURE_CLIENT_SECRET']), str(os.environ['AZURE_TENANT_ID']))

        # self.credentials = ServicePrincipalCredentials(
        #     client_id=os.environ['AZURE_CLIENT_ID'],
        #     secret=os.environ['AZURE_CLIENT_SECRET'],
        #     tenant=os.environ['AZURE_TENANT_ID']
        # )
        self.client = ResourceManagementClient(self.credentials, self.subscription_id)

    def deploy(self, azure_location, stack_type, stack_params={}):
        """Deploy the template to a resource group."""
        self.client.resource_groups.create_or_update(
            self.resource_group_name,
            {
                'location': azure_location
            }
        )

        template_file_name = None
        if stack_type == "scanner":
            template_file_name = "FSS-Scanner-Stack-Template.json"
        elif stack_type == "storage":
            template_file_name = "FSS-Storage-Stack-Template.json"

        template_path = os.path.join(os.path.dirname(__file__), 'templates', template_file_name)
        with open(template_path, 'r') as template_file_fd:
            template = json.load(template_file_fd)

        print("\n\n\nTemplate - \n\n\t" + str(template))

        parameters = {
            'vmName': 'azure-deployment-sample-vm'
        }
        parameters.update(stack_params)
        parameters = {k: {'value': v} for k, v in parameters.items()}

        deployment_properties = {
            'mode': DeploymentMode.incremental,
            'template': template,
            'parameters': parameters
        }

        deployment_async_operation = self.client.deployments.create_or_update(
            self.resource_group_name,
            self.resource_group_name + '-deployment',
            deployment_properties
        )
        deployment_async_operation.wait()

    def destroy(self):
        """Destroy the given resource group"""
        self.client.resource_groups.delete(self.resource_group_name)