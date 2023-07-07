# Trend Micro Cloud One File Storage Security Post-Scan Actions with Amazon SNS Topic

## Overview
This readme.md file provides an explanation of how Trend Micro Cloud One File Storage Security post-scan actions rely on the Amazon SNS topic. It also discusses the use of SNS subscription filter policies to optimize AWS Lambda function invocation, reducing false positives and unnecessary cloud spend.

To learn more about efficient event processing with SNS Subscription Filter policy for lambda check out [here](https://medium.com/dev-genius/efficient-event-processing-with-sns-subscription-filter-policy-for-lambda-d86dc19fd4f0).

---

## AWS Resource Links
- [Amazon SNS Documentation](https://aws.amazon.com/sns/)
- [AWS Lambda Documentation](https://aws.amazon.com/lambda/)
- [AWS CloudFormation Documentation](https://aws.amazon.com/cloudformation/)

## Trend Micro Links
- [Trend Micro Cloud One File Storage Security](https://www.trendmicro.com/en_us/business/products/hybrid-cloud/file-storage-security.html)
- [Trend Micro Cloud One Documentation](https://cloudone.trendmicro.com/docs/)

---

## SNS Subscription Filters Solutions

### SNS Solution Filter Example Use Case 1

- FSS was deployed as well as with the quarantine post-scan action. The Quarantine lambda function would be invoked every time a scan would occur[malicous, no issues found, or scan code errors]. To restrict invocations of this Lambda to invoke only when malicous events occur was desired. 

- This SNS subscription filter ensures that the event corresponds to a malicious event detected during the scan.

```json
{
   "scanning_result":{
      "Findings":{
         "malware":[
            {
               "exists":true
            }
         ]
      }
   }
}
```
---

### SNS Solution Filter Use Case Example 2

- With FSS deployed and using Promote/Quarantine plugin; Files that failed to be scanned would still be acted on by the p/q lambda function. To ensure that the file/object is only moved if error "Code" does not exist. 

- This filter ensures that the AWS Lambda function is not triggered when scan error codes exist on FSS Scans. 

```json
{
   "scanning_result":{
         "Codes":[
            {
               "exists": false
            }
         ]
      }
  }
```
