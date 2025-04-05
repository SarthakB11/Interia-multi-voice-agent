from datetime import datetime, timedelta
from config.config import LeadStatus, MAX_CALL_ATTEMPTS, RETRY_DELAY_MINUTES
from .airtable_utils import AirtableManager
from .vapi_utils import VapiManager

class N8NWorkflowHandler:
    def __init__(self):
        self.airtable = AirtableManager()
        self.vapi = VapiManager()

    def handle_trigger_workflow(self):
        """Handle the trigger workflow that initiates calls."""
        # Get leads that need to be called
        leads = self.airtable.get_leads_to_call()
        
        for lead in leads:
            lead_id = lead['id']
            fields = lead['fields']
            
            # Update lead status to in-progress
            self.airtable.update_lead_status(lead_id, LeadStatus.IN_PROGRESS)
            
            # Initiate call
            call_response = self.vapi.initiate_call(
                customer_number=fields.get('Mobile'),
                first_name=fields.get('First Name'),
                lead_id=lead_id
            )
            
            if not call_response:
                # If call initiation failed, mark as failed
                self.airtable.update_lead_status(
                    lead_id,
                    LeadStatus.FAILED,
                    summary="Failed to initiate call"
                )

    def handle_call_result(self, webhook_data):
        """Handle the webhook callback from Vapi with call results."""
        lead_id = webhook_data.get('metadata', {}).get('lead_id')
        if not lead_id:
            print("No lead_id in webhook data")
            return
        
        ended_reason = webhook_data.get('ended_reason')
        transcript = webhook_data.get('transcript')
        
        # Log call details first
        self.airtable.log_call({
            'callproviderID': webhook_data.get('id'),
            'phonenumberID': webhook_data.get('phoneNumberId'),
            'customernumber': webhook_data.get('customer', {}).get('number'),
            'started': webhook_data.get('started'),
            'ended': webhook_data.get('ended'),
            'milliseconds': webhook_data.get('duration'),
            'cost_llm': webhook_data.get('cost', {}).get('llm'),
            'cost_tts': webhook_data.get('cost', {}).get('tts'),
            'cost_stt': webhook_data.get('cost', {}).get('stt'),
            'cost_total': webhook_data.get('cost', {}).get('total'),
            'ended_reason': ended_reason,
            'transcript': transcript,
            'lead_id': lead_id
        })
        
        # Get current lead details
        lead = self.airtable.get_lead_by_id(lead_id)
        current_attempt = lead['fields'].get('Attempt', 0)
        
        # Check if call was answered successfully
        if self._is_call_answered(ended_reason, transcript):
            self.airtable.update_lead_status(
                lead_id,
                LeadStatus.CALLED,
                summary=self._extract_call_summary(transcript)
            )
            return
        
        # Handle voicemail or unanswered calls
        if self._is_voicemail_or_unanswered(ended_reason):
            if current_attempt < MAX_CALL_ATTEMPTS - 1:
                # Increment attempt and retry
                next_attempt = current_attempt + 1
                self.airtable.update_lead_status(
                    lead_id,
                    LeadStatus.TO_BE_CALLED,
                    attempt=next_attempt
                )
            else:
                # Max attempts reached
                self.airtable.update_lead_status(
                    lead_id,
                    LeadStatus.FAILED,
                    summary="Unreachable after maximum attempts"
                )
        else:
            # Other failure cases
            self.airtable.update_lead_status(
                lead_id,
                LeadStatus.FAILED,
                summary=f"Call failed: {ended_reason}"
            )

    def _is_call_answered(self, ended_reason, transcript):
        """Check if the call was answered successfully."""
        voicemail_indicators = ['voicemail', 'leave a message', 'after the tone']
        failed_reasons = [
            'customer_did_not_answer',
            'assistant_error',
            'pipeline_error',
            'failed_to_connect',
            'unknown_reason',
            'voicemail'
        ]
        
        if ended_reason.lower() in failed_reasons:
            return False
            
        if transcript:
            if any(indicator in transcript.lower() for indicator in voicemail_indicators):
                return False
                
        return True

    def _is_voicemail_or_unanswered(self, ended_reason):
        """Check if the call reached voicemail or was unanswered."""
        voicemail_reasons = [
            'voicemail',
            'customer_did_not_answer',
            'customer_busy'
        ]
        return ended_reason.lower() in voicemail_reasons

    def _extract_call_summary(self, transcript):
        """Extract a summary from the call transcript."""
        # In a real implementation, you might want to use OpenAI or another
        # service to generate a proper summary
        if not transcript:
            return "No transcript available"
        return transcript[:500] + "..." if len(transcript) > 500 else transcript 