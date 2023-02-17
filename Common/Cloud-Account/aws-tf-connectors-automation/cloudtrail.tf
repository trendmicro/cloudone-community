resource "aws_cloudformation_stack" "cloudtrail" {
  depends_on = [null_resource.add_ws_connector]
  name = "TrendmicroCloudtrailClient"
  template_body = file("cloudtrail.yaml")
  capabilities = [ "CAPABILITY_AUTO_EXPAND", "CAPABILITY_IAM", "CAPABILITY_NAMED_IAM" ]
  parameters = {
    APIVersion = "v1"
    S3BucketName = "cloud-trail-client-stack-template-prod-us-east-1"
    ServiceURL = "https://cloudtrail.us-1.cloudone.trendmicro.com"
    ServiceToken = var.service_token
  }
}
