from pyairtable import Api
from config.config import AIRTABLE_API_KEY, AIRTABLE_BASE_ID, LeadStatus

class AirtableManager:
    def __init__(self):
        self.api = Api(AIRTABLE_API_KEY)
        self.base = self.api.base(AIRTABLE_BASE_ID)
        self.leads_table = self.base.table('Leads')
        self.calls_table = self.base.table('Call Records')

    def get_leads_to_call(self, limit=10):
        """Get leads that need to be called."""
        formula = f"AND({{Status}} = '{LeadStatus.TO_BE_CALLED}', {{Attempt}} < 2)"
        return self.leads_table.all(formula=formula, max_records=limit)

    def update_lead_status(self, record_id, status, attempt=None, summary=None):
        """Update lead status and optionally increment attempt count."""
        fields = {'Status': status}
        if attempt is not None:
            fields['Attempt'] = attempt
        if summary is not None:
            fields['Summary'] = summary
        return self.leads_table.update(record_id, fields)

    def log_call(self, call_data):
        """Log call details in the Call Records table."""
        return self.calls_table.create({
            'callproviderID': call_data.get('callproviderID'),
            'phonenumberID': call_data.get('phonenumberID'),
            'customernumber': call_data.get('customernumber'),
            'type': 'outbound',
            'started': call_data.get('started'),
            'ended': call_data.get('ended'),
            'milliseconds': call_data.get('milliseconds'),
            'cost_llm': call_data.get('cost_llm', 0),
            'cost_tts': call_data.get('cost_tts', 0),
            'cost_stt': call_data.get('cost_stt', 0),
            'cost_total': call_data.get('cost_total', 0),
            'ended_reason': call_data.get('ended_reason'),
            'transcript': call_data.get('transcript'),
            'lead_id': call_data.get('lead_id')
        })

    def get_lead_by_id(self, record_id):
        """Get lead details by record ID."""
        return self.leads_table.get(record_id)

    def get_lead_by_phone(self, phone_number):
        """Get lead details by phone number."""
        formula = f"{{Mobile}} = '{phone_number}'"
        records = self.leads_table.all(formula=formula)
        return records[0] if records else None 