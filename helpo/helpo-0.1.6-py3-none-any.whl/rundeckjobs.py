import requests
import json
import os
from loguru import logger


class RundeckJobs(object):
    def __init__(
            self,
            uptimerobot_api_url: str = "https://api.uptimerobot.com/v2/getMonitors",
    ):
        self.uptimerobot_api_url = uptimerobot_api_url

    @logger.catch
    def search_uptimerobot(
            self,
            deployment_action=os.environ.get('RD_OPTION_DEPLOYMENT_ACTION'),
            uptimerobot_api_key=os.environ.get("RD_OPTION_UPTIMEROBOT_API_KEY"),
            fqdn=os.environ.get("RD_OPTION_FQDN"),
            force_apply=os.environ.get('RD_OPTION_FORCE_APPLY')):
        if deployment_action != 'apply':
            print("Skipping website hosting check as deployment action is not apply")
            exit(0)

        url = self.uptimerobot_api_url

        payload = f"api_key={uptimerobot_api_key}&search={fqdn}"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        if len(json.loads(response.text)["monitors"]) == 0:
            print(f"{fqdn} seems to be a new site, skipping!")
            exit(0)
        elif force_apply == "true":
            print("Force apply is requested, ignoring check results")
            exit(0)
        else:
            print(f"{fqdn} is alive, want to force redeployment? then change option `force_apply` value to `true`")
            exit(1)
