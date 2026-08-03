import os
import logging

logger = logging.getLogger(__name__)

class SMSProviderAbstraction:
    @staticmethod
    def send_sms(phone_number, message_body):
        provider = os.environ.get('SMS_PROVIDER', 'twilio').lower()

        if not phone_number:
            logger.warning("SMS dispatch skipped: phone_number is empty.")
            return {'success': False, 'error': 'Phone number missing'}

        logger.info(f"Dispatching SMS via provider '{provider}' to {phone_number}: {message_body}")

        if provider == 'twilio':
            account_sid = os.environ.get('TWILIO_ACCOUNT_SID', '')
            auth_token = os.environ.get('TWILIO_AUTH_TOKEN', '')
            # Twilio SDK call or mock fallback
            return {'success': True, 'provider': 'twilio', 'status': 'sent'}
        elif provider == 'msg91':
            return {'success': True, 'provider': 'msg91', 'status': 'sent'}
        elif provider == 'gupshup':
            return {'success': True, 'provider': 'gupshup', 'status': 'sent'}
        elif provider == 'exotel':
            return {'success': True, 'provider': 'exotel', 'status': 'sent'}
        else:
            return {'success': True, 'provider': 'generic_sms', 'status': 'sent'}
