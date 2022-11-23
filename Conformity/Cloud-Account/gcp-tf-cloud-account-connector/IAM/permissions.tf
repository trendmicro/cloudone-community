variable "permissions" {
  description = "The permissions to grant to the role"
  type        = list(string)
  default     = [ "bigquery.datasets.get", "bigquery.tables.get", "apikeys.keys.list", "serviceusage.services.list", "resourcemanager.projects.get", "resourcemanager.projects.getIamPolicy", "iam.serviceAccounts.get","accessapproval.settings.get", "cloudkms.keyRings.list", "cloudkms.cryptoKeys.list", "cloudkms.cryptoKeys.getIamPolicy", "cloudkms.locations.list", "compute.firewalls.list", "compute.networks.list", "compute.subnetworks.list", "storage.buckets.list", "storage.buckets.getIamPolicy", "compute.instances.list", "compute.images.list",  "compute.images.getIamPolicy", "compute.projects.get", "cloudsql.instances.list", "compute.backendServices.list", "compute.globalForwardingRules.list", "compute.targetHttpsProxies.list", "compute.targetSslProxies.list", "compute.sslPolicies.list", "compute.urlMaps.list", "dns.managedZones.list", "dns.policies.list", "dataproc.clusters.list", "container.clusters.list", "logging.sinks.list", "logging.logMetrics.list", "monitoring.alertPolicies.list", "pubsub.topics.list", "resourcemanager.projects.get", "orgpolicy.policy.get" ]
}



