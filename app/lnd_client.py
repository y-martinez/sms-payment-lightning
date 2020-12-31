import requests
from django.conf import settings
from typing import Dict


class LndRestClient:
    def __init__(self):
        endpoint = settings.LND_REST["ENDPOINT"]
        endpoint = endpoint[:-1] if endpoint.endswith("/") else endpoint
        endpoint = (
            "https://" + endpoint if not endpoint.startswith("http") else endpoint
        )
        self.endpoint = endpoint

        self.auth = {"Grpc-Metadata-macaroon": settings.LND_REST["MACAROON"]}
        self.cert = settings.LND_REST["CERT"]

    def new_address(self) -> Dict:
        try:
            response = requests.get(
                f"{self.endpoint}/v1/newaddress", headers=self.auth, verify=self.cert
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            return {
                "error": errh.response.text,
                "status_code": errh.response.status_code,
            }
        except requests.exceptions.RequestException:
            return {
                "error": f"Unable to connect to {self.endpoint}",
                "status_code": 500,
            }

        return response.json()
