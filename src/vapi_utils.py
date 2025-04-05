import requests
from config.config import (
    VAPI_API_KEY,
    VAPI_ASSISTANT_ID,
    VAPI_PHONE_NUMBER_ID,
    VOICEMAIL_DETECTION_TIMEOUT
)

class VapiManager:
    def __init__(self):
        self.base_url = "https://api.vapi.ai"
        self.headers = {
            "Authorization": f"Bearer {VAPI_API_KEY}",
            "Content-Type": "application/json"
        }

    def initiate_call(self, customer_number, first_name, lead_id):
        """Initiate an outbound call using Vapi."""
        endpoint = f"{self.base_url}/call"
        
        payload = {
            "assistantId": VAPI_ASSISTANT_ID,
            "phoneNumberId": VAPI_PHONE_NUMBER_ID,
            "customer": {
                "number": customer_number,
                "name": first_name
            },
            "metadata": {
                "lead_id": lead_id
            },
            "config": {
                "voicemailConfig": {
                    "enabled": True,
                    "timeout": VOICEMAIL_DETECTION_TIMEOUT,
                    "provider": "google"  # Can be 'twilio', 'google', or 'openai'
                }
            }
        }

        try:
            response = requests.post(endpoint, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error initiating call: {str(e)}")
            return None

    def get_call_status(self, call_id):
        """Get the status of a specific call."""
        endpoint = f"{self.base_url}/call/{call_id}"
        
        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting call status: {str(e)}")
            return None

    def update_assistant_webhook(self, webhook_url):
        """Update the assistant's webhook URL."""
        endpoint = f"{self.base_url}/assistant/{VAPI_ASSISTANT_ID}"
        
        payload = {
            "serverURL": webhook_url,
            "serverMessages": ["endOfCallReport"]
        }

        try:
            response = requests.patch(endpoint, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error updating webhook: {str(e)}")
            return None 