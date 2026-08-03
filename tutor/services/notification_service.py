from tutor.models import Notification, NotificationPreference
from tutor.services.sms_service import SMSProviderAbstraction
from tutor.services.whatsapp_service import WhatsAppReportService
from tutor.services.email_service import EmailDigestService

class NotificationEngine:
    @staticmethod
    def send_notification(user, title, message, notification_type='goal_achieved', channel='in_app'):
        prefs, _ = NotificationPreference.objects.get_or_create(user=user)

        # Create DB Notification
        notif = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            channel=channel
        )

        dispatch_results = {'in_app': True}

        if channel == 'sms' or prefs.enable_sms:
            if prefs.phone_number:
                res = SMSProviderAbstraction.send_sms(prefs.phone_number, f"{title}: {message}")
                dispatch_results['sms'] = res.get('success', False)

        if channel == 'whatsapp' or prefs.enable_whatsapp:
            if prefs.whatsapp_number:
                res = WhatsAppReportService.send_whatsapp_summary(
                    whatsapp_number=prefs.whatsapp_number,
                    child_name=user.username,
                    completion_pct=85,
                    study_time_mins=60,
                    hw_status="Completed",
                    reading_score=90,
                    speaking_score=88,
                    next_goal="Practice Fractions"
                )
                dispatch_results['whatsapp'] = res.get('success', False)

        if channel == 'email' or prefs.enable_email:
            if user.email:
                res = EmailDigestService.send_parent_email_digest(
                    parent_email=user.email,
                    child_name=user.username,
                    summary_html=f"<h3>{title}</h3><p>{message}</p>"
                )
                dispatch_results['email'] = res.get('success', False)

        return {
            'success': True,
            'notification_id': notif.id,
            'dispatch_results': dispatch_results
        }
