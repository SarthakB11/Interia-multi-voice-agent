from decouple import config

# Airtable Configuration
AIRTABLE_API_KEY = config('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = config('AIRTABLE_BASE_ID')

# Vapi Configuration
VAPI_API_KEY = config('VAPI_API_KEY')
VAPI_ASSISTANT_ID = config('VAPI_ASSISTANT_ID')
VAPI_PHONE_NUMBER_ID = config('VAPI_PHONE_NUMBER_ID')

# Gemini Configuration
GEMINI_API_KEY = config('GEMINI_API_KEY')

# Twilio Configuration
TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN')

# n8n Configuration
N8N_WEBHOOK_URL = config('N8N_WEBHOOK_URL')

# Lead Status Constants
class LeadStatus:
    TO_BE_CALLED = "TBC"
    IN_PROGRESS = "In-Progress"
    CALLED = "Called"
    FAILED = "Failed"
    CALLBACK_REQUESTED = "Called - Callback Requested"
    INCORRECT_CONTACT = "Failed - Incorrect Contact"
    ABUSIVE = "Failed - Abusive"

# Call Attempt Configuration
MAX_CALL_ATTEMPTS = 2
RETRY_DELAY_MINUTES = 1

# Voicemail Detection Configuration
VOICEMAIL_DETECTION_TIMEOUT = 15  # seconds

# Budget Thresholds (in lakhs)
MIN_BUDGET_LAKHS = 30 
