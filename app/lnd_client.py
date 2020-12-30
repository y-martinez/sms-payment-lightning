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
            r = requests.get(
                f"{self.endpoint}/v1/newaddresss", headers=self.auth, verify=self.cert
            )
            r.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            return {
                "error": errh.response.text,
                "status_code": errh.response.status_code,
            }
        except requests.exceptions.Timeout:
            return {
                "error": f"Unable to connect to {self.endpoint}",
                "status_code": 408,
            }
        except requests.exceptions.TooManyRedirects:
            return {
                "error": f"Unable to connect to {self.endpoint}",
                "status_code": 429,
            }
        except requests.exceptions.RequestException:
            return {
                "error": f"Unable to connect to {self.endpoint}",
                "status_code": 500,
            }

        return r.json()