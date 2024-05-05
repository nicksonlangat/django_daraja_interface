import base64
from datetime import datetime

import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth


class MpesaDarajaHandler:
    """
    Mpesa handler to interface with Safaricom's
    Daraja APIs
    """

    def __init__(self, token_generation_url, stk_url):
        super().__init__()
        self.token_generation_url = token_generation_url

        self.stk_url = stk_url

    def decode_password(self):
        time = datetime.now().strftime("%Y%m%d%H%M%S")
        data_to_encode = (
            str(settings.BUSINESS_SHORT_CODE) + settings.MPESA_PASS_KEY + time
        )
        return base64.b64encode(data_to_encode.encode()).decode("utf-8")

    def stk_initiation_time(self):
        return datetime.now().strftime("%Y%m%d%H%M%S")

    def create_token(self):
        response = requests.get(
            self.token_generation_url,
            auth=HTTPBasicAuth(settings.CONSUMER_KEY, settings.CONSUMER_SECRET),
        )
        response_body = response.json()
        return response_body["access_token"]

    def register_urls(self):
        access_token = self.create_token()
        headers = {"Authorization": "Bearer %s" % access_token}
        payload = {
            "ShortCode": settings.SHORTCODE,
            "ResponseType": "Completed",
            "ConfirmationURL": str(self.confirmation_url),
            "ValidationURL": str(self.validation_url),
        }
        response = requests.post(self.regitration_url, json=payload, headers=headers)

        return response.json()

    def lipa_na_mpesa_online(
        self, phone_number, amount, account_reference, description, callback
    ):
        # self.register_urls()
        access_token = self.create_token()
        headers = {"Authorization": "Bearer %s" % access_token}
        request = {
            "BusinessShortCode": settings.BUSINESS_SHORT_CODE,
            "Password": self.decode_password(),
            "Timestamp": self.stk_initiation_time(),
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone_number,
            "PartyB": settings.BUSINESS_SHORT_CODE,
            "PhoneNumber": phone_number,
            "CallBackURL": callback,
            "AccountReference": account_reference,
            "TransactionDesc": description,
        }

        response = requests.post(self.stk_url, json=request, headers=headers)
        return response.json()
