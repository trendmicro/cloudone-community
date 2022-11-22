import urllib3
import argparse
import json

# Arguments
parser = argparse.ArgumentParser(description='Download Deployment Scripts')
parser.add_argument("--apikey", required=True, type=str, help="Cloud One API Key")
parser.add_argument("--c1region", required=True, type=str, help="Cloud One Account Region")
parser.add_argument("--platform", required=True, type=str, help="OS Platform")
args = parser.parse_args()


http = urllib3.PoolManager()

api_key = args.apikey
c1_region = args.c1region
platform = args.platform.lower()



api_endpoint = "https://workload."+c1_region+".cloudone.trendmicro.com/api/agentdeploymentscripts"


headers={
            "Authorization": "ApiKey " + api_key,
            "Api-Version": "v1",
            "Content-Type": "application/json"
        }

data={
            "platform": platform,
            "validateCertificateRequired": False,
            "validateDigitalSignatureRequired": False,
            "activationRequired": True
        }

def ws_download_script():
    try:
        if platform == "linux":
            print("Downloading Linux Deployment Script")
            response = http.request('POST', api_endpoint, headers=headers, body=json.dumps(data))
            response_json = json.loads(response.data)
            answer = response_json['scriptBody']
            script = open("ws.sh", "w")
            script.write(answer)
            script.close()
        elif platform == "windows": 
            print("Downloading Windows Deployment Script")
            response = http.request('POST', api_endpoint, headers=headers, body=json.dumps(data))
            response_json = json.loads(response.data)
            answer = response_json['scriptBody']
            script = open("ws.ps1", "w")
            script.write(answer)
            script.close()
    except Exception as e:
        print("Error: ", e)

ws_download_script()