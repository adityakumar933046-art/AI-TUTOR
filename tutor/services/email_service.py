import logging
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

class EmailDigestService:
    @staticmethod
    def send_parent_email_digest(parent_email, child_name, summary_html):
        if not parent_email:
            return {'success': False, 'error': 'Parent email missing'}

        subject = f"EduVerse AI Kids: Daily Learning Progress for {child_name}"
        
        try:
            send_mail(
                subject=subject,
                message=f"Daily Summary for {child_name}: Please view HTML email.",
                html_message=summary_html,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@eduverse.ai'),
                recipient_list=[parent_email],
                fail_silently=True
            )
            return {'success': True, 'channel': 'email', 'recipient': parent_email}
        except Exception as e:
            logger.error(f"Failed to send email digest: {e}")
            return {'success': False, 'error': str(e)}
